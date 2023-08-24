using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Net.Http;
using System.Net;
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

        public async Task LogConnectionAsync(ConnectionLog connectionLog) {
            try
            {
                var response = await _client.PostAsJsonAsync("monitoring/post/log", connectionLog);
                if (response.StatusCode != HttpStatusCode.OK)
                {
                    _logger.LogError("LogConnectionAsync returned " + response.StatusCode);
                }
            }
            catch (Exception e)
            {
                _logger.LogError("LogConnectionAsync failed. " + e);
            }
        }

        public async Task<string> GetConnectedUsersRecentAsync()
        {
            try
            {
                var response = await _client.GetAsync("monitoring/get/recents"); // monitoring/get/all
                if (response.StatusCode != HttpStatusCode.OK)
                {
                    _logger.LogError("GetConnectedUsersRecentAsync returned " + response.StatusCode);
                    return null;
                }
                else
                {
                    return await response.Content.ReadAsStringAsync();
                }
            }
            catch (Exception e)
            {
                _logger.LogError("GetConnectedUsersRecentAsync failed. " + e);
                return null;
            }
        }
    }
    
}