using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Microsoft.EntityFrameworkCore;
using testservice.Models;
using testservice.Services;
using System.Text;

namespace testservice.Controllers
{
    [Route("test")]
    [ApiController]
    public class TestController : ControllerBase
    {
        private RabbitMQService _mqService;
        private ILogger<TestController> _logger;
        private DbService _dbService;
        private StorageService _storageService;

        public TestController(ILogger<TestController> logger, RabbitMQService mqService, DbService dbService, StorageService storageService)
        {
            _mqService = mqService;
            _logger = logger;
            _dbService = dbService;
            _storageService = storageService;
        }

        [HttpGet("{userEmail?}")]
        public ActionResult<IAsyncEnumerable<TestRun>> OnGetList(
            [FromRoute]string userEmail, [FromQuery]Guid? submissionId, [FromQuery]Guid? taskId)
        {
            var queryable = _dbService.Tests.AsQueryable();
            if (userEmail != null)
            {
                queryable = queryable.Where(test => test.CreatedBy == userEmail);
            }

            if (submissionId != null)
            {
                 queryable = queryable.Where(
                     test => test.SubmissionId == submissionId.ToString());
            }
            if (taskId != null)
            {
                queryable = queryable.Where(
                    test => test.TaskId == taskId.ToString());
            }
            return Ok(queryable.OrderByDescending(test => test.CreatedAt).Take(20).AsAsyncEnumerable());
        }

        [HttpGet("{userEmail}/{testid:guid}")]
        public async Task<ActionResult<TestRun>> OnGetAsync(
            [FromRoute] string userEmail, [FromRoute] Guid testid)
        {
            _logger.LogTrace("Retrieving concrete test {testid} {email}", testid, userEmail);
            var testRun = await _dbService.Tests.FirstOrDefaultAsync(
                test => test.Id == testid.ToString() && test.CreatedBy == userEmail);
            if (testRun == null)
            {
                _logger.LogWarning("Test was not found {id}", testid);
                return NotFound();
            }

            if (testRun.Status != TestRunConstants.TestFinished)
            {
                return Ok(testRun);
            }
            // Now we have to download contents
            try
            {
                var studentJson = await _storageService.DownloadResultAsync(
                    _storageService.CreateName(
                        userEmail: userEmail,
                        testId: testid.ToString(),
                        fileName: TestRunConstants.FileStudents));
                testRun.Students = Encoding.UTF8.GetString(studentJson);

                var teachersJson = await _storageService.DownloadResultAsync(
                    _storageService.CreateName(
                        userEmail: userEmail,
                        testId: testid.ToString(),
                        fileName: TestRunConstants.FileTeachers));
                testRun.Teachers = Encoding.UTF8.GetString(teachersJson);

                return Ok(testRun);
            }
            catch(Exception e)
            {
                _logger.LogError(
                    "Error while downloading results for test {id} {email} {e}", testid, userEmail, e);
                return StatusCode(500);
            }
        }

        [HttpPost]
        public async Task<ActionResult> OnPostAsync([FromBody]TestRequest testRequest)
        {
            _logger.LogTrace("Creating new test case");
            TestCase testCase = await _dbService.Cases.FirstOrDefaultAsync(@case => @case.Id == testRequest.TestCaseId);
            if (testCase == null)
            {
                _logger.LogWarning("Invalid test case id supplied {id}", testRequest.TestCaseId);
                return BadRequest();
            }
            // -------------
            if (testRequest.Counted)
            {
                _logger.LogTrace("Run is counted, counting test runs");
                var testedCount = await _dbService.Tests.Where(
                    test => test.TestCaseId == testCase.Id && test.CreatedBy == testRequest.CreatedBy).CountAsync();
                if (testedCount >= testCase.MaxRuns)
                {
                    _logger.LogTrace("Test runs all spent {} of {}, quitting", testedCount, testCase.MaxRuns);
                    return StatusCode(402);
                }
            }
            // Test runs are ok
            var testRun = new TestRun(testRequest);
            _dbService.Tests.Add(testRun);
            await _dbService.SaveChangesAsync();
            _logger.LogTrace("Test run was created in DB");
            // Put request to queue
            TestRequestMessage mqMessage = new() {
                ContentUrl = testRequest.ContentUrl,
                DockerImage = testCase.DockerImage,
                MetaData = testRun.Id
            };
            _mqService.Publish(mqMessage.ToJson());
            // TODO: Have publisher ack
            _logger.LogTrace("Test run was published to MQ");
            return Ok();
        }

    }
}
