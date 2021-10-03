using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading.Tasks;
using System.Web;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using presentation.Model;

namespace presentation.Services
{
    public class SubmissionService
    {
        public SubmissionService(ILogger<SubmissionService> logger, IConfiguration config)
        {
            _client.BaseAddress = new Uri(config["SUBMISSION_SERVICE"]);
            _client.DefaultRequestHeaders.Accept.Clear();
            _client.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
            _logger = logger;
        }

        // TODO: This is for admin only, create also user function
        public async Task<IList<Submission>> GetSubmissionsAsync()
        {
            _logger.LogTrace("Requesting submissions from service");
            try
            {
                HttpResponseMessage message = await _client.GetAsync("/submission/");
                if (message.IsSuccessStatusCode)
                {
                    var submissions = await message.Content.ReadAsAsync<List<Submission>>();
                    _logger.LogTrace($"Retrieved {submissions.Count} submissions");
                    return submissions;
                }
                else
                {
                    _logger.LogWarning($"Code {message.StatusCode} reason {message.ReasonPhrase}");
                    throw new OperationFailedException();
                }
            }
            catch (TaskCanceledException e)
            {
                _logger.LogWarning("Get submissions timeout/cancel {e}", e);
                throw new OperationFailedException();
            }
            catch (Exception e)
            {
                _logger.LogError("Get submissions failed {e}", e);
                throw new OperationFailedException();
            }
        }

        public async Task<Submission> CreateSubmissionAsync(Submission submission)
        {
            try
            {
                _logger.LogTrace("Posting new {submission}", submission);
                // TODO: We should distinguish deadline errors from operation errors
                HttpResponseMessage message = await _client.PostAsJsonAsync("/submission/", submission);
                if (message.IsSuccessStatusCode)
                {
                    _logger.LogTrace("Submission POST returned success");
                    return await message.Content.ReadAsAsync<Submission>();
                }
                else
                {
                    string stringJsonError = await message.Content.ReadAsStringAsync();
                    var jsonOptions = new JsonSerializerOptions
                    {
                        PropertyNameCaseInsensitive = true
                    };
                    RestError restError = JsonSerializer.Deserialize<RestError>(stringJsonError, jsonOptions);
                    _logger.LogWarning("Post submission returned {status}, errors: {errorList}", (int)message.StatusCode, restError.GetErrors());
                    throw new OperationFailedException();
                }
            }
            catch (Exception e)
            {
                _logger.LogWarning("Create submission failed {e}", e);
                throw new OperationFailedException();
            }
        }

        // Returns null on not found, or throws OperationFailedException
        public async Task<Submission> GetSubmissionAsync(string userEmail, string submissionId, bool urlOnly = false)
        {
            string query = "?contentFormat=";
            if (urlOnly)
            {
                query += "url";
            }

            _logger.LogTrace("Requesting submission {email} / {id}", userEmail, submissionId);
            HttpResponseMessage response = await _client.GetAsync(
                $"/submission/{HttpUtility.UrlEncode(userEmail)}/{HttpUtility.UrlEncode(submissionId)}/{query}");
            if (!response.IsSuccessStatusCode)
            {
                if (((int)response.StatusCode) == 404)
                {
                    // Probably somebody just trying to browse other submissions
                    _logger.LogWarning("Submission not found on server");
                    return null;
                }
                else
                {
                    // We log error here, because there is something wrong
                    _logger.LogError("Request failed {code} {e}", response.StatusCode, response.ReasonPhrase);
                    throw new OperationFailedException();
                }
            }

            try
            {
                return await response.Content.ReadFromJsonAsync<Submission>();
            }
            catch(Exception e)
            {
                _logger.LogError("Cannot parse returned submission, {e}", e);
            }
            throw new OperationFailedException();
        }


        private HttpClient _client = new HttpClient();
        private ILogger<SubmissionService> _logger = null;
    }

}
