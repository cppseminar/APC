using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text;
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
            _client.BaseAddress = new Uri(config["API_GATEWAY"]);
            _client.DefaultRequestHeaders.Accept.Clear();
            _client.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
            _logger = logger;
        }

        public async Task<IList<Submission>> GetUserSubmissionsAsync(string userEmail, int pageNumber=0)
        {
            userEmail ??= "";
            userEmail = HttpUtility.UrlEncode(userEmail);
            _logger.LogTrace("Requesting submissions from service");
            try
            {
                HttpResponseMessage message = await _client.GetAsync($"/submission/{userEmail}?PageNumber={pageNumber}");
                if (message.IsSuccessStatusCode)
                {
                    var submissions = await message.Content.ReadAsAsync<List<Submission>>();
                    _logger.LogTrace("Retrieved {} submissions", submissions.Count);
                    return submissions;
                }
                else
                {
                    _logger.LogWarning("Code {} reason {}", message.StatusCode, message.ReasonPhrase);
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

        public async Task<int> GetNumberOfPages(string userEmail)
        {
            userEmail = HttpUtility.UrlEncode(userEmail ?? "");
            _logger.LogTrace("Requesting submissions from service");
            try
            {
                HttpResponseMessage message = null; 
                if (userEmail == ""){
                    message = await _client.GetAsync($"/submission/count");
                }
                else   {
                    message = await _client.GetAsync($"/submission/{userEmail}/count");
                }
                    
                if (message.IsSuccessStatusCode)
                {
                    var numberOfPages = await message.Content.ReadAsAsync<int>();
                    _logger.LogTrace("Retrieved {} submissions", numberOfPages);
                    return numberOfPages;
                }
                else
                {
                    _logger.LogWarning("Code {} reason {}", message.StatusCode, message.ReasonPhrase);
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

        public async Task<byte[]> DownloadTaskSubmissionsAsync(string taskId)
        {
            _logger.LogTrace("Requesting submissions from service for task {taskId}", taskId);
            try
            {
                HttpResponseMessage message = await _client.GetAsync($"/submission/task/{taskId}");
                if (message.IsSuccessStatusCode)
                {
                    var submissions = await message.Content.ReadAsAsync<List<Dictionary<string, string>>>();
                    _logger.LogTrace("Retrieved {} submissions", submissions.Count);

                    using var memoryStream = new MemoryStream();
                    using (var archive = new ZipArchive(memoryStream, ZipArchiveMode.Create, true))
                    {
                        for (int i = 0; i < submissions.Count; i++)
                        {
                            var email = submissions[i]["userEmail"];
                            var submissionId = submissions[i]["submissionId"];

                            _logger.LogTrace("Requesting submission {submissionId} for user {email}", submissionId, email);
                            message = await _client.GetAsync($"/submission/{email}/{submissionId}?contentFormat=file");
                            if (message.IsSuccessStatusCode)
                            {
                                var file = archive.CreateEntry($"{email}_{submissionId}.cpp");

                                using var entryStream = file.Open();
                                using var streamWriter = new StreamWriter(entryStream);

                                _logger.LogTrace("Writting content to zip file {fileName}", file.Name);

                                var data = await message.Content.ReadAsAsync<Submission>();
                                streamWriter.Write(data.Content);
                            }
                        }
                    }

                    return memoryStream.ToArray();
                }
                else
                {
                    _logger.LogWarning("Code {} reason {}", message.StatusCode, message.ReasonPhrase);
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

        public async Task<IList<Submission>> GetSubmissionsAsync()
        {
            return await GetUserSubmissionsAsync(null);
        }

        public async Task<Submission> CreateSubmissionAsync(Submission submission)
        {
            try
            {
                _logger.LogTrace("Posting new {submission}", submission);
                // TODO: We should distinguish deadline errors from operation errors
                HttpContent content = new StringContent(JsonSerializer.Serialize(submission), Encoding.UTF8, "application/json");
                HttpResponseMessage message = await _client.PostAsync("/submission/", content);
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
                    _logger.LogWarning("Post submission {obj} returned {status}, errors: {errorList}", JsonSerializer.Serialize(submission), (int)message.StatusCode, restError.GetErrors());
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

        private readonly HttpClient _client = new();
        private readonly ILogger<SubmissionService> _logger = null;
    }

}
