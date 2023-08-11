using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using MongoDB.Bson;
using submissions.Models;
using submissions.Services;

namespace submissions.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class SubmissionController : Controller
    {
        public SubmissionController(
            SubmissionsService submissions,
            ILogger<SubmissionController> logger,
            StorageService storage)
        {
            _submissions = submissions;
            _logger = logger;
            _storage = storage;
        }

        [HttpGet]
        public async Task<ActionResult<List<Submission>>> OnGetAsync([FromQuery] int PageNumber=0)
        {
            try
            {
                System.Console.WriteLine("PAge number in all submissions "+ PageNumber);
                _logger.LogTrace("Retrieving all submissions");
                System.Console.WriteLine("V obycajnom getAsync");
                return Ok(await _submissions.GetAsync(_pageSize,PageNumber));
            }
            catch (Exception e)
            {
                _logger.LogError("Error during retrieval of data. {e}", e);
                return StatusCode(500);  // Internal error
            }
        }

        [HttpGet("task/{taskId}")]
        public async Task<ActionResult<List<SubmissionsService.GetForTaskItem>>> OnGetForTaskAsync(string taskId)
        {
            try
            {
                _logger.LogTrace("Retrieving all submissions for task {taskId}", taskId);

                return Ok(await _submissions.GetForTask(taskId));
            }
            catch (Exception e)
            {
                _logger.LogError("Error during retrieval of data. {e}", e);
                return StatusCode(500);  // Internal error
            }
        }

        [HttpGet("{email}")]
        public async Task<ActionResult<List<Submission>>> OnGetAsync(string email, [FromQuery]string taskId, [FromQuery] int PageNumber=0)
        {
            try
            {
                _logger.LogTrace("Retrieving all submissions for user {email} with task id {taskId}", email, taskId);

                return Ok(await _submissions.GetForUserAsync(email, taskId, _pageSize, PageNumber));
            }
            catch (System.FormatException e)
            {
                _logger.LogError("Wrong input format. {e}", e);
                return StatusCode(400);
            }
            catch (Exception e)
            {
                _logger.LogError("Error during retrieval of data. {e}", e);
                return StatusCode(500);  // Internal error
            }
        }

        [HttpGet("{email}/count")]
        public async Task<ActionResult<List<Submission>>> OnGetAsync(string email, [FromQuery]string taskId)
        {
            try
            {
                _logger.LogTrace("Retrieving all submissions for user {email} with task id {taskId}", email, taskId);
                return Ok(await _submissions.GetCountAsyncUser(email, taskId, _pageSize));
            }
            catch (System.FormatException e)
            {
                _logger.LogError("Wrong input format. {e}", e);
                return StatusCode(400);
            }
            catch (Exception e)
            {
                _logger.LogError("Error during retrieval of data. {e}", e);
                return StatusCode(500);  // Internal error
            }
        }
        [HttpGet("count")]
        public async Task<ActionResult<List<Submission>>> CountAllDocuments([FromQuery]string taskId)
        {
            string email = "";
            try
            {
                _logger.LogTrace("Retrieving all submissions for user {email} with task id {taskId}", email, taskId);
                return Ok(await _submissions.GetCountAsyncUser(email, taskId, _pageSize));
            }
            catch (System.FormatException e)
            {
                _logger.LogError("Wrong input format. {e}", e);
                return StatusCode(400);
            }
            catch (Exception e)
            {
                _logger.LogError("Error during retrieval of data. {e}", e);
                return StatusCode(500);  // Internal error
            }
        }



        // https://www.yogihosting.com/aspnet-core-api-controllers/

        [HttpGet("{email}/{submissionId}")]
        public async Task<ActionResult<Submission>> GetSubmissionAsync(
            string email, string submissionId, [FromQuery]string contentFormat)
        {
            try
            {
                _logger.LogTrace("Retrieving submission {id} for {email}", submissionId, email);
                Submission result = await _submissions.GetAsync(submissionId);

                if (result.UserEmail != email)
                {
                    _logger.LogWarning("Submission email isn't right");
                    return NotFound();
                }

                _logger.LogTrace("Submission found in db, retrieving blob");

                List<string> blobPath = new() { email, submissionId };
                    
                if (contentFormat == "url")
                {
                    _logger.LogTrace("Retrieving blob as sas url");
                    result.Content = _storage.GetUrlBlob(blobPath);
                }
                else
                {
                    _logger.LogTrace("Retrieving blob as binary data");
                    result.Content = (await _storage.DownloadBlobAsync(blobPath)).ToString();
                }

                _logger.LogTrace("Retrieved blob data successfuly");
                return Ok(result);
            }
            catch (System.FormatException e)
            {
                _logger.LogError("Wrong input format. {e}", e);
                return StatusCode(400);
            }
            catch (System.InvalidOperationException e) // this is the exception for not found
            {
                _logger.LogError("Submission id not found. {e}", e);
                return NotFound();
            }
            catch (Exception e)
            {
                _logger.LogError("Error during data retrieval. {e}", e);
                return StatusCode(500);  // Internal error
            }
        }

        [HttpPost]
        public async Task<ActionResult<Submission>> Create([FromBody] Submission submission)
        {
            if (submission.UserEmail != StorageService.NormalizeFileName(submission.UserEmail))
            {
                _logger.LogWarning(
                    "Rejecting submission create, due to invalid email {email}", submission.UserEmail);
                return BadRequest();
            }

            if (submission.Content == null)
            {
                _logger.LogWarning("Content cannot be empty on create.");
                return BadRequest();
            }

            if (!ObjectId.TryParse(submission.TaskId, out _))
            {
                _logger.LogWarning("TaskId must be valid ObjectId.");
                return BadRequest();
            }

            _logger.LogTrace("Saving submission {obj}", JsonSerializer.Serialize(submission));

            await _submissions.CreateAsync(submission);

            _logger.LogInformation("Submission saved to mongo, now to blob");

            try
            {
                await _storage.UploadBlobAsync(
                    new List<string> { submission.UserEmail, submission.Id.ToString() },
                    new BinaryData(submission.Content)
                    );

                return Created("N/A", submission);
            }
            catch (Exception e)
            {
                // TODO: Test if this deletion really works
                _logger.LogWarning("Unable to save to blob, reverting db. {e}", e);
                await _submissions.RemoveAsync(submission.Id);

                // If there is exception, let it be some error
                _logger.LogTrace("Reverted db succesfully");
                return StatusCode(500);
            }
        }

        private readonly SubmissionsService _submissions = null;
        private readonly ILogger<SubmissionController> _logger = null;
        private readonly StorageService _storage = null;
        private readonly int _pageSize = 10;
    }
}
