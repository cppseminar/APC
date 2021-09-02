using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using presentation.Model;

namespace presentation.Services
{
    public class TaskService
    {
        public TaskService(ILogger<TaskService> logger)
        {
            _logger = logger;
            _client.BaseAddress = new Uri(_url);
            _client.DefaultRequestHeaders.Accept.Clear();
            _client.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
        }

        public async Task<bool> CreateTaskAsync(TaskModel taskModel)
        {
            _logger.LogTrace("POSTing new task model");
            try
            {
                HttpResponseMessage response = await _client.PostAsJsonAsync("tasks/v1/", taskModel, new JsonSerializerOptions
                {
                    IgnoreNullValues = true
                });
                if (!response.IsSuccessStatusCode)
                {
                    string stringJsonError = await response.Content.ReadAsStringAsync();
                    var jsonOptions = new JsonSerializerOptions()
                    {
                        PropertyNameCaseInsensitive = true
                    };
                    RestError restError = JsonSerializer.Deserialize<RestError>(stringJsonError, jsonOptions);
                    _logger.LogTrace("Task POST failed {code} {errors}", (int)response.StatusCode, restError.GetErrors());
                    return false;
                }
                _logger.LogTrace("NewTask POST was suceessful");
                return true;
            }
            catch (Exception e)
            {
                _logger.LogWarning("Create task POST failed {error}", e);
            }
            return false;
        }

        private ILogger<TaskService> _logger = null;
        private const string _url = "http://submissions.local:5004";
        private HttpClient _client = new HttpClient();
    }
}
