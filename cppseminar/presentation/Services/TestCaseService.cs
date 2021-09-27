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
    public class TestCaseService
    {
        private HttpClient _client = new HttpClient();
        private ILogger<TestCaseService> _logger;

        public TestCaseService(ILogger<TestCaseService> logger, IConfiguration config)
        {
            _logger = logger;
            _client.BaseAddress = new Uri(config["TEST_SERVICE"]);
            _client.DefaultRequestHeaders.Accept.Clear();
            _client.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
        }

        public async Task<List<TestCaseRest>> GetAll()
        {
            return await GetTestCases(null);
        }

        public async Task<List<TestCaseRest>> GetByTask(string taskId)
        {
            return await GetTestCases(taskId);
        }

        private async Task<List<TestCaseRest>> GetTestCases(string taskId)
        {
            _logger.LogTrace("Retrieving test cases for task? {id}", taskId);
            var queryParams = HttpUtility.ParseQueryString(string.Empty);
            if (taskId != null)
            {
                queryParams["taskId"] = taskId;
            }
            HttpResponseMessage result = await _client.GetAsync($"cases/?{queryParams}");

            if(!result.IsSuccessStatusCode)
            {
                _logger.LogWarning("Request returned status code {code}", result.StatusCode);
                return new List<TestCaseRest>();
            }
            try
            {
                return await result.Content.ReadAsAsync<List<TestCaseRest>>();
            }
            catch(Exception e)
            {
                _logger.LogWarning("Error during parsing test case list {e}", e);
            }
            return new List<TestCaseRest>();

        }

        public async Task CreateCase(TestCaseRest testCase)
        {
            _logger.LogTrace("Creating new test case {case}", testCase);
            try
            {
                for (int i = 0; i < 5; i++)
                {
                    var result = await _client.PostAsJsonAsync("cases/", testCase);
                    if (result.IsSuccessStatusCode)
                    {
                       _logger.LogTrace("Test case creation returned success code");
                        return;
                    }
                    _logger.LogWarning("Test case creation returned code {code}", result.StatusCode);
                }
                throw new OperationFailedException("Too many retries");
            }
            catch(Exception e)
            {
                _logger.LogWarning("Creating new test case failed with: {e}", e);
                throw new OperationFailedException();
            }
        }
    }
}
