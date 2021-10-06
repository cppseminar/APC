using System;
using System.Collections.Generic;
using System.Linq;
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
            _client.BaseAddress = new Uri(config["TEST_SERVICE"]);
            _client.DefaultRequestHeaders.Accept.Clear();
            _client.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
        }
        public async Task CreateTest(TestRequestRest testRequest)
        {
            _logger.LogTrace("Posting new test run {run}", testRequest);
            try
            {
                var result = await _client.PostAsJsonAsync("test/", testRequest);
                if (result.IsSuccessStatusCode)
                {
                    return;
                }
                _logger.LogWarning("Failed creating test, with status {code}", result.StatusCode);
            }
            catch(Exception e)
            {
                _logger.LogWarning("Errror during test creation {e}", e);
                throw new OperationFailedException();
            }
        }

        public async Task<List<TestRun>> GetTestsForUserAsync(string userName, string submissionId)
        {
            return await RetrieveTestsAsync(userName: userName, submissionId: submissionId);
        }

        public async Task<TestRun> GetOneTest(string userEmail, Guid testId)
        {
            _logger.LogTrace("Retrieving test run {user} {id}", userEmail, testId);
            string uri = $"test/{HttpUtility.UrlEncode(userEmail)}/{testId.ToString()}";
            try
            {
                var response = await _client.GetAsync(uri);
                response.EnsureSuccessStatusCode();
                return await response.Content.ReadAsAsync<TestRun>();
            }
            catch(Exception e)
            {
                _logger.LogWarning("Error while retrieving test run {e}");
                throw new OperationFailedException();
            }
        }

        private async Task<List<TestRun>> RetrieveTestsAsync(
            string userName = null, string taskId = null, string submissionId = null)
        {
            var query = "?";
            if (submissionId != null)
            {
                query += $"submissionId={HttpUtility.UrlEncode(submissionId)}&";
            }
            var response = await _client.GetAsync(
                $"test/{HttpUtility.UrlEncode(userName ?? string.Empty)}" + query);
            return await response.Content.ReadAsAsync<List<TestRun>>();
        }
    }
}
