using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System.Text.Json;
using monitoringservice.Model;
using monitoringservice.Services;

namespace monitoringservice.Controllers;

[Route("monitoring")]
[ApiController]
public class MonitoringController : ControllerBase
{
    private readonly ILogger<MonitoringController> _logger;
    private readonly StorageService _service;

    public MonitoringController(ILogger<MonitoringController> logger, StorageService service)
    {
        _logger = logger;
        _service = service;
    }

    [HttpGet("get/recents")]
    public async Task<ActionResult<List<ConnectionLog>>> OnGetAsync()
    {
        try
        {
            return await _service.getConnectionLogsAsync();
        }
        catch (Exception e)
        {
            _logger.LogError("Exception occured while retrieving all ConnectionLog records. " + e);
            return StatusCode(500);
        }
    }

    [HttpPost("post/log")]
    public async Task<ActionResult> LogConnection([FromBody] ConnectionLog connectionLog)
    {
        if (connectionLog.UserEmail == null || connectionLog.Timestamp == null)
        {
            return BadRequest();
        }
        else
        {
            try
            {
                await _service.setConnectionlogAsync(connectionLog);
                return Ok();
            }
            catch (Exception e)
            {
                _logger.LogError("Exception occured while logging user connection. " + e);
                return StatusCode(500);
            }
        }
    }
}
