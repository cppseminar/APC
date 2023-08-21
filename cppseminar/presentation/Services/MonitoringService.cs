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
        public MonitoringService(ILogger<MonitoringService> logger, IConfiguration config)
        {
            _client.BaseAddress = new Uri(config["API_GATEWAY"]);
            _client.DefaultRequestHeaders.Accept.Clear();
            _client.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
            _logger = logger;
        }
        public async Task<List<ConnectionLog>> Test(){
            var connectionLog = new ConnectionLog();
            connectionLog.UserEmail = "Test user";
            connectionLog.Timestamp = DateTime.Now;
            List<ConnectionLog> list = new List<ConnectionLog>
            {
                connectionLog
            };
            return list;

        }
        private readonly HttpClient _client = new();
        private readonly ILogger<MonitoringService> _logger = null;
    }
    
}