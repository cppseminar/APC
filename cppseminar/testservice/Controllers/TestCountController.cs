using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System.Threading.Tasks;
using testservice.Models;
using testservice.Services;

namespace testservice.Controllers
{
    [Route("testcount")]
    [ApiController]
    public class TestCountController : ControllerBase
    {
        private readonly ILogger<TestRunsController> _logger;
        private readonly TestRunsService _runsService;

        public TestCountController(ILogger<TestRunsController> logger, TestRunsService runsService)
        {
            _logger = logger;
            _runsService = runsService;
        }

        /* Count how many times student started test */
        [HttpGet("{userEmail}/{testCaseId}")]
        public async Task<ActionResult<TestRunCount>> OnGetTestCountAsync([FromRoute] string userEmail, [FromRoute] string testCaseId)
        {
            _logger.LogTrace("Counting # of testruns for {userEmail} - {testCaseId}", userEmail, testCaseId);
            long count = await _runsService.GetCountAsync(userEmail, testCaseId);

            var result = new TestRunCount()
            {
                Count = (int)count,
                UserEmail = userEmail,
                TestCaseId = testCaseId
            };
            return Ok(result);
        }
    }
}
