using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
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
    }
}
