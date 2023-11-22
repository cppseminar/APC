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

        public async Task<List<TestRun>> GetTestsAsync(string userEmail, string submissionId)
        {
            userEmail = !string.IsNullOrEmpty(userEmail) ? userEmail : null;
            submissionId = !string.IsNullOrEmpty(submissionId) ? submissionId : null;

            return await RetrieveTestsAsync(userName: userEmail, submissionId: submissionId);
        }

        public async Task<TestRun> GetOneTest(string userEmail, string testId)
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
            string userName = null, string submissionId = null)
        {
            var query = "?";
            if (submissionId != null)
            {
                query += $"submissionId={HttpUtility.UrlEncode(submissionId)}&";
            }

            var response = await _client.GetAsync(
                $"test/{HttpUtility.UrlEncode(userName)}/" + query);
            return await response.Content.ReadAsAsync<List<TestRun>>();
        }
        // Get used runs on one test
        public async Task<long> GetTestRunsAsync(string userEmail, string testId)
        {
            userEmail = !string.IsNullOrEmpty(userEmail) ? userEmail : null;
            testId = !string.IsNullOrEmpty(testId) ? testId : null;
            try {
                var response = await _client.GetAsync($"/test/count/{userEmail}/{testId}");
                if (response.IsSuccessStatusCode) {
                    var count = await response.Content.ReadAsAsync<long>();
                    _logger.LogTrace("Retrieved {} runs", count);
                    return count;
                }
                else {
                     _logger.LogWarning("Code {} reason {}", response.StatusCode, response.ReasonPhrase);
                    throw new OperationFailedException();
                }
            }
            catch (Exception e){
                 _logger.LogError("Get test runs failed {e}", e);
                throw new OperationFailedException();
            }  
        }
        public async Task<bool> SetCountedTestRun(string testRunId, bool value){
             testRunId= !string.IsNullOrEmpty(testRunId) ? testRunId : null;
             try{
                var response = await _client.PostAsJsonAsync($"/test/setCounted/{testRunId}", value);
                if (response.IsSuccessStatusCode) {
                    return true;
                }
                else {
                     _logger.LogWarning("Code {} reason {}", response.StatusCode, response.ReasonPhrase);
                    throw new OperationFailedException();
                }
             }
             catch (Exception e){
                 _logger.LogError("Get test runs failed {e}", e);
                throw new OperationFailedException();
            }  
        }
    }
}
