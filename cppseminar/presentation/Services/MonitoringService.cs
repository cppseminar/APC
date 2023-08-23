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
    public class MonitoringService
    {
        private readonly HttpClient _client = new HttpClient();
        private readonly ILogger<MonitoringService> _logger = null;

        public MonitoringService(ILogger<MonitoringService> logger, IConfiguration config)
        {
            _client.BaseAddress = new Uri(config["API_GATEWAY"]);
            _client.DefaultRequestHeaders.Accept.Clear();
            _client.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
            _logger = logger;            
        }

        public async Task<List<ConnectionLog>> GetConnectedUsersRecentAsync()
        {
            var response = await _client.GetAsync("monitoring/get/recents"); // monitoring/get/all
            //var responseJson = await response.Content.ReadAsStringAsync();
            return await response.Content.ReadAsAsync<List<ConnectionLog>>();
            // System.Console.WriteLine(responseJson);
            // return responseJson;
        }
    }
    
}