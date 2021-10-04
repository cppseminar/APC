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

namespace testservice.Controllers
{
    [Route("test")]
    [ApiController]
    public class TestController : ControllerBase
    {
        private RabbitMQService _mqService;
        private ILogger<TestController> _logger;
        private DbService _dbService;

        public TestController(ILogger<TestController> logger, RabbitMQService mqService, DbService dbService)
        {
            _mqService = mqService;
            _logger = logger;
            _dbService = dbService;
        }

        [HttpGet("{userEmail?}")]
        public ActionResult<IAsyncEnumerable<TestRun>> OnGetList(
            [FromRoute]string userEmail, [FromQuery]Guid? submissionId)
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
            return Ok(queryable.OrderBy(test => test.CreatedAt).Take(20).AsAsyncEnumerable());
        }

        [HttpGet("{userEmail}/{testid:guid}")]
        public async Task<ActionResult<TestRun>> OnGetAsync(string userEmail, Guid testid)
        {
            _logger.LogTrace("Retrieving concrete test {testid} {email}", testid, userEmail);
            var testRun = await _dbService.Tests.FirstOrDefaultAsync(
                test => test.Id == testid.ToString() && test.CreatedBy == userEmail);
            if (testRun == null)
            {
                _logger.LogWarning("Test was not found {id}", testid);
                return NotFound();
            }

            return Ok(testRun);
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
            // TODO: Count test runs for this case

            // ----------
            // Test runs are ok
            var testRun = new TestRun(testRequest);
            _dbService.Tests.Add(testRun);
            await _dbService.SaveChangesAsync();
            _logger.LogTrace("Test run was created in DB");
            // Put request to queue
            TestRequestMessage mqMessage = new() {
                ContentUrl = testRequest.ContentUrl,
                DockerImage = testCase.DockerImage,
                Metadata = testRun.Id
            };
            _mqService.Publish(mqMessage.ToJson());
            // TODO: Have publisher ack
            _logger.LogTrace("Test run was published to MQ");
            return Ok();
        }

    }
}
