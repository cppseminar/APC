using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using System.Web;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using presentation.Model;

namespace presentation.Services
{
    public class TestService
    {
        private ILogger<TestCaseService> _logger;
        private HttpClient _client = new ();

        public TestService(ILogger<TestCaseService> logger, IConfiguration config)
        {
            _logger = logger;
            _client.BaseAddress = new Uri(config["API_GATEWAY"]);
            _client.DefaultRequestHeaders.Accept.Clear();
            _client.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
        }
        // Returns true if test was created. False if you don't have enough test runs
        // and throws OperationFailed if something else happens
        public async Task<bool> CreateTest(TestRequestRest testRequest)
        {
            _logger.LogTrace("Posting new test run {run}", testRequest);
            try
            {
                var result = await _client.PostAsJsonAsync("test/", testRequest);
                if (result.IsSuccessStatusCode)
                {
                    return true;
                }
                else if (result.StatusCode == HttpStatusCode.PaymentRequired)
                {
                    return false;
                }
                _logger.LogWarning("Failed creating test, with status {code}", result.StatusCode);
                throw new OperationFailedException();
            }
            catch(Exception e)
            {
                _logger.LogWarning("Errror during test creation {e}", e);
                throw new OperationFailedException();
            }
        }

        public async Task<List<TestRun>> GetTestsAsync(string userEmail, string taskId, string submissionId)
        {
            userEmail = !string.IsNullOrEmpty(userEmail) ? userEmail : null;
            taskId = !string.IsNullOrEmpty(taskId) ? taskId : null;
            submissionId = !string.IsNullOrEmpty(submissionId) ? submissionId : null;

            return await RetrieveTestsAsync(userName: userEmail, submissionId: submissionId, taskId: taskId);
        }

        public async Task<TestRun> GetOneTest(string userEmail, Guid testId)
        {
            _logger.LogTrace("Retrieving test run {user} {id}", userEmail, testId);
            string uri = $"test/{HttpUtility.UrlEncode(userEmail)}/{testId}";
            try
            {
                var response = await _client.GetAsync(uri);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadAsAsync<TestRun>();
            }
            catch(Exception e)
            {
                _logger.LogWarning("Error while retrieving test run {e}", e);
                throw new OperationFailedException();
            }
        }

        public async Task<List<TestRun>> RetrieveTestsAsync(
            string userName = null, string taskId = null, string submissionId = null)
        {
            var query = "?";
            if (submissionId != null)
            {
                query += $"submissionId={HttpUtility.UrlEncode(submissionId)}&";
            }
            if (taskId != null)
            {
                query += $"taskId={HttpUtility.UrlEncode(taskId)}&";
            }

            var response = await _client.GetAsync(
                $"test/{HttpUtility.UrlEncode(userName)}/" + query);
            return await response.Content.ReadAsAsync<List<TestRun>>();
        }
    }
}
