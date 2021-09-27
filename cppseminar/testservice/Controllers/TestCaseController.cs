using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using testservice.Models;
using testservice.Services;

namespace testservice.Controllers
{
    [Route("cases")]
    [ApiController]
    public class TestCaseController : ControllerBase
    {
        private ILogger<TestCaseController> _logger;
        private DbService _dbService;

        public TestCaseController(ILogger<TestCaseController> logger, DbService dbService)
        {
            _logger = logger;
            _dbService = dbService;
        }

        [HttpGet]
        public ActionResult<IAsyncEnumerable<TestCase>> OnGetListAsync([FromQuery]string taskId)
        {
            _logger.LogTrace("Retrieving case list for task? {id}", taskId);
            try
            {
                if (taskId == null)
                {
                    return Ok(_dbService.Cases.AsAsyncEnumerable());
                }
                return Ok(_dbService.Cases.Where(x => x.TaskId == taskId).AsAsyncEnumerable());
            }
            catch(Exception e)
            {
                _logger.LogWarning("Error while retrieving from db {e}", e);
                return StatusCode(500);
            }
        }

        [HttpGet("{caseId}")]
        public async Task<ActionResult<TestCase>> OnGetCaseAsync(string caseId)
        {
            _logger.LogTrace("Retrieving test case  {id}", caseId);
            try
            {
                var result = await _dbService.Cases.FirstOrDefaultAsync(x => x.Id == caseId);
                if (result == null)
                {
                    _logger.LogWarning("Case {id} not found", caseId);
                    return NotFound();
                }
                return Ok(result);
            }
            catch (Exception e)
            {
                _logger.LogWarning("Error while retrieving test case {id} {e}", caseId, e);
                return StatusCode(500);
            }
        }

        [HttpPost]
        public async Task<ActionResult> PostAsync([FromBody]TestCase testCase)
        {
            testCase.CreatedAt = DateTime.UtcNow;
            testCase.Id = Guid.NewGuid().ToString();

            _logger.LogTrace("Creating new test case {obj}", testCase);
            _dbService.Cases.Add(testCase);

            for (int i = 0; i < 5; i++)
            {
                try
                {
                    await _dbService.SaveChangesAsync();
                    _logger.LogTrace("Test case saved succesfully");
                    return Created("N/A", testCase);
                }
                catch (Exception e)
                {
                    _logger.LogWarning("Failed saving changes with error {e}", e);
                    await Task.Delay(i * 1000);
                }
            }
            return StatusCode(500);
        }
    }
}
