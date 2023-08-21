using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading.Tasks;
using presentation.Services;
using presentation.Model;

namespace presentation.Controllers
{
    [Route("monitoring")]
    [ApiController]
    public class MonitoringController : ControllerBase
    {
        private readonly ILogger<MonitoringController> _logger;
        private readonly MonitoringService _monitoringService;

        public MonitoringController(ILogger<MonitoringController> logger, MonitoringService monitoringService)
        {
            _logger = logger;
            _monitoringService = monitoringService;
        }

        [HttpGet]
        public async Task<ActionResult<List<ConnectionLog>>> OnGet()
        {
            if(!User.IsAdmin()){
                System.Console.WriteLine("Unauthorized request");
                return StatusCode(401);
            }
            System.Console.WriteLine("caf a fsdfasdfsfsdf");
            

            try
            {
                var connectionLog = await _monitoringService.Test();
                return connectionLog;
            }
            catch (Exception e)
            {
                _logger.LogWarning("Error during retrieval of data, {e}", e);
                return StatusCode(500);  // Internal error
            }
        }

        
    }
}


