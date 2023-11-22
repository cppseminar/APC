using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading.Tasks;
using testservice.Model;
using testservice.Models;
using testservice.Services;

namespace testservice.Controllers;

[Route("cases")]
[ApiController]
public class TestCasesController : ControllerBase
{
    private readonly ILogger<TestCasesController> _logger;
    private readonly TestCasesService _testCases;

    public TestCasesController(ILogger<TestCasesController> logger, TestCasesService testCases)
    {
        _logger = logger;
        _testCases = testCases;
    }

    [HttpGet]
    public async Task<ActionResult<List<TestCase>>> OnGet([FromQuery] string taskId)
    {
        _logger.LogTrace("Get test cases for task {id}", taskId);

        try
        {
            if (taskId == null)
            {
                return await _testCases.GetAsync(30);
            }
            else
            {
                return await _testCases.GetForTaskAsync(taskId, 30);
            }
        }
        catch (System.FormatException e)
        {
            _logger.LogWarning("Wrong input format, taskId {id}. {e}", taskId, e);
            return StatusCode(400);
        }
        catch (Exception e)
        {
            _logger.LogWarning("Error during retrieval of data, taskId {id}. {e}", taskId, e);
            return StatusCode(500);  // Internal error
        }
    }

    [HttpGet("{caseId}")]
    public async Task<ActionResult<TestCase>> OnGetById(string caseId)
    {
        _logger.LogTrace("Get test case {id}", caseId);

        try
        {
            return await _testCases.GetAsync(caseId);
        }
        catch (System.FormatException e)
        {
            _logger.LogWarning("Wrong input format, caseId {id}. {e}", caseId, e);
            return StatusCode(400);
        }
        catch (Exception e)
        {
            _logger.LogWarning("Error during retrieval of data, caseId {id}. {e}", caseId, e);
            return StatusCode(500);  // Internal error
        }
    }

    [HttpPost]
    public async Task<ActionResult> PostAsync([FromBody] TestCase testCase)
    {
        _logger.LogTrace("Creating new test case {obj}", JsonSerializer.Serialize(testCase));

        try
        {
            await _testCases.CreateAsync(testCase);

            _logger.LogTrace("Test case saved succesfully");

            return Created("N/A", testCase);
        }
        catch (Exception e)
        {
            _logger.LogWarning("Failed saving changes with error {e}", e);

            return StatusCode(500);
        }
    }
    [HttpPost("update/{testCaseId}")]
    public async Task<ActionResult> UpdateAsync([FromRoute] string testCaseId, [FromBody] TestCaseUpdate testCase)
    {
        _logger.LogTrace("Updating new test case {obj}", JsonSerializer.Serialize(testCase));
        
        try
        {
            await _testCases.UpdateTestCase(testCaseId, testCase);

            _logger.LogTrace("Test case updated succesfully");

            return Ok();
        }
        catch (Exception e)
        {
            _logger.LogWarning("Failed saving changes with error {e}", e);

            return StatusCode(500);
        }
    }
}
