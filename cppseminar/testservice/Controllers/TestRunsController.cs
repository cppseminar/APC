using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using testservice.Models;
using testservice.Services;

namespace testservice.Controllers;

[Route("test")]
[ApiController]
public class TestRunsController : ControllerBase
{
    private readonly RabbitMQService _mqService;
    private readonly ILogger<TestRunsController> _logger;
    private readonly TestRunsService _testRuns;
    private readonly TestCasesService _testCases;
    private readonly StorageService _storageService;

    public TestRunsController(
        ILogger<TestRunsController> logger,
        RabbitMQService mqService,
        TestRunsService testRuns,
        TestCasesService testCases,
        StorageService storageService)
    {
        _mqService = mqService;
        _logger = logger;
        _testRuns = testRuns;
        _testCases = testCases;
        _storageService = storageService;
    }

    [HttpGet("{userEmail?}")]
    public async Task<ActionResult<List<TestRun>>> OnGetAsync(
        [FromRoute] string userEmail, [FromQuery] string submissionId)
    {
        _logger.LogTrace("Retrieving concrete test taskid submissionid {subm} user {user}", submissionId, userEmail);

        try
        {
            return Ok(await _testRuns.GetAsync(userEmail, submissionId, 20));
        }
        catch (FormatException e)
        {
            _logger.LogWarning("Wrong input format, taskId submissionId {subm} user {user}. {e}", submissionId, userEmail, e);
            return StatusCode(400);
        }
        catch (Exception e)
        {
            _logger.LogWarning("Error during retrieval of data, taskId submissionId {subm} user {user}. {e}", submissionId, userEmail, e);
            return StatusCode(500);  // Internal error
        }
    }

    [HttpGet("{userEmail}/{testId}")]
    public async Task<ActionResult<TestRun>> OnGetByIdAsync(
        [FromRoute] string userEmail, [FromRoute] string testId)
    {
        _logger.LogTrace("Retrieving concrete test {test} {user}", testId, userEmail);

        TestRun testRun;

        try
        {
            testRun = await _testRuns.GetAsync(testId);
            if (testRun.CreatedBy != userEmail)
            {
                _logger.LogWarning("Test run id {test} do not correspond to email {user}", testId, userEmail);
                return NotFound();
            }
        }
        catch (FormatException e)
        {
            _logger.LogWarning("Wrong input format, testId {test} user {user}. {e}", testId, userEmail, e);
            return StatusCode(400);
        }
        catch (Exception e)
        {
            _logger.LogError("Error retrieving data for run id {test} {e}", testId, e);
            return StatusCode(500);
        }

        if (testRun.Status != TestStatus.Finished)
        {
            return Ok(testRun);
        }

        // Now we have to download contents
        try
        {
            var studentJson = await _storageService.DownloadResultAsync(
                _storageService.CreateName(
                    userEmail: userEmail,
                    testId: testId,
                    fileName: TestRunConstants.FileStudents));
            testRun.Students = Encoding.UTF8.GetString(studentJson);

            var teachersJson = await _storageService.DownloadResultAsync(
                _storageService.CreateName(
                    userEmail: userEmail,
                    testId: testId,
                    fileName: TestRunConstants.FileTeachers));
            testRun.Teachers = Encoding.UTF8.GetString(teachersJson);

            return Ok(testRun);
        }
        catch (Exception e)
        {
            _logger.LogError(
                "Error while downloading results for test {test} {user} {e}", testId, userEmail, e);
            return StatusCode(500);
        }
    }

    [HttpPost]
    public async Task<ActionResult> OnPostAsync([FromBody] TestRun testRun)
    {
        _logger.LogTrace("Creating new test run {obj}.", JsonSerializer.Serialize(testRun));

        TestCase testCase;

        try
        {
            testCase = await _testCases.GetAsync(testRun.TestCaseId);
        }
        catch (Exception e)
        {
            _logger.LogError("Invalid test case id supplied {case}. {e}", testRun.TestCaseId, e);
            return BadRequest();
        }

        if (testRun.Counted)
        {
            _logger.LogTrace("Run is counted, counting test runs");
            var testedCount = await _testRuns.GetCountAsync(testRun.CreatedBy, testCase.Id);

            if (testedCount >= testCase.MaxRuns)
            {
                _logger.LogTrace("Test runs all spent {count} of {max}, quitting", testedCount, testCase.MaxRuns);
                return StatusCode(402);
            }
        }

        // Test runs are ok
        await _testRuns.CreateAsync(testRun);

        _logger.LogTrace("Test run was created in DB");
        // Put request to queue
        TestRequestMessage mqMessage = new()
        {
            ContentUrl = testRun.ContentUrl,
            DockerImage = testCase.DockerImage,
            MetaData = testRun.Id
        };

        _logger.LogTrace("Sending test request {obj}", JsonSerializer.Serialize(mqMessage));

        _mqService.Publish(mqMessage.ToJson());
        // TODO: Have publisher ack

        _logger.LogTrace("Test run was published to MQ");

        return Ok();
    }
    //counts number of used tests
    [HttpGet("count/{userEmail}/{testId}")]
    public async Task<ActionResult<long>> CountTestRuns([FromRoute] string userEmail, [FromRoute] string testId)
    {
        System.Console.WriteLine("Tu som v test run controller");
        _logger.LogTrace("Retrieving concrete test {test} {user}", testId, userEmail);

        long CountedRuns;

        try
        {
            CountedRuns = await _testRuns.GetCountAsync(userEmail, testId);
        }
        catch (FormatException e)
        {
            _logger.LogWarning("Wrong input format, userEmail {userEmail} testId {testId}. {e}", userEmail, testId, e);
            return StatusCode(400);
        }
        catch (Exception e)
        {
            _logger.LogError("Error retrieving data for run id {test} {e}", testId, e);
            return StatusCode(500);
        }

        return CountedRuns;
    }

    [HttpPost("setCounted/{testRunId}")]
    public async Task<ActionResult> UpdateTestRunCounted([FromRoute] string testRunId, [FromBody] bool countedValue)
    {
        if (testRunId == null){
            return BadRequest();
        }
        try
        {
            
            var UpdateResult = await _testRuns.SetCounted(testRunId, countedValue);
            if (UpdateResult.IsAcknowledged){
                return StatusCode(200);
            }
            else 
                return StatusCode(500);
        }
        catch (Exception e)
        {
            _logger.LogError("Invalid test run id supplied {case}. {e}", testRunId, e);
            return BadRequest();
        }
    }
}



