using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using System.Web;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Polly;
using presentation.Model;

namespace presentation.Services
{
    public class TestCaseService
    {
        private readonly HttpClient _client = new();
        private readonly ILogger<TestCaseService> _logger;

        public TestCaseService(ILogger<TestCaseService> logger, IConfiguration config)
        {
            _logger = logger;
            _client.BaseAddress = new Uri(config["API_GATEWAY"]);
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

            try
            {
                HttpResponseMessage result = await _client.GetAsync($"cases/?{queryParams}");
                if (!result.IsSuccessStatusCode)
                {
                    _logger.LogWarning("Request returned status code {code}", result.StatusCode);
                    return new List<TestCaseRest>();
                }
                return await result.Content.ReadAsAsync<List<TestCaseRest>>();
            }
            catch (Exception e)
            {
                _logger.LogWarning("Error during parsing test case list {e}", e);
            }
            return null;

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
            catch (Exception e)
            {
                _logger.LogWarning("Creating new test case failed with: {e}", e);
                throw new OperationFailedException();
            }
        }

        public async Task<TestCaseRest> GetById(string caseId)
        {
            _logger.LogTrace("Retrieving test case {id}", caseId);
            string uriPath = $"cases/{HttpUtility.UrlEncode(caseId)}";


            var retryPolicy = Policy
                .Handle<Exception>()
                .WaitAndRetryAsync(
                    new[] { TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(3) },
                    onRetry: (exception, retryCount) =>
                    {
                        _logger.LogTrace("Retrying failed request error {e}", exception);
                    });

            var fallbackPolicy = Policy
                .Handle<Exception>()
                .FallbackAsync(
                    fallbackAction: async token => { await Task.Delay(0, token); },
                    onFallbackAsync: async (exception) =>
                    {
                        _logger.LogWarning("Failed {e}", exception);
                        await Task.Delay(0); // Get rid of warning
                    }).WrapAsync(retryPolicy);

            TestCaseRest testCase = null;

            await fallbackPolicy.ExecuteAsync(async () =>
            {
                var result = await _client.GetAsync(uriPath);
                if ((int)result.StatusCode == 404)
                {
                    return;
                }
                result.EnsureSuccessStatusCode();
                testCase = await result.Content.ReadAsAsync<TestCaseRest>();
                

            });
            return testCase;
        }
        public async Task UpdateTest(string testCaseId, TestCaseRest testCase){
            _logger.LogTrace("Updating test case {case}", testCase);
            try
            {
                var result = await _client.PostAsJsonAsync($"/cases/update/{testCaseId}", testCase);
                System.Console.WriteLine(result);
                if (result.IsSuccessStatusCode)
                {
                    _logger.LogTrace("Test case update returned success code");
                    return;
                }
                else{
                    throw new OperationFailedException("Operation failed");
                }
            }
            catch (Exception e)
            {
                _logger.LogWarning("Creating new test case failed with: {e}", e);
                throw new OperationFailedException();
            }
        }
    }
}
