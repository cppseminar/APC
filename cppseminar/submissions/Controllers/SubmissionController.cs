using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using submissions.Data;
using submissions.Models;
using submissions.Services;

namespace submissions.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class SubmissionController : Controller
    {
        public SubmissionController(CosmosContext context, ILogger<SubmissionController> logger, StorageService storage)
        {
            _context = context;
            _logger = logger;
            _storage = storage;
        }

        [HttpGet]
        public IEnumerable<Submission> Index()
        {
            return _context.Submissions.OrderByDescending(submission => submission.SubmittedOn);
        }

        [HttpGet("{email}")]
        public IEnumerable<Submission> IndexForUser(string email) => _context.Submissions.Where(s => s.UserEmail == email)
                                                                                         .OrderBy(s => s.SubmittedOn)
                                                                                         .Take(30);


        // https://www.yogihosting.com/aspnet-core-api-controllers/

        [HttpGet("{email}/{submissionId}")]
        public async Task<ActionResult<SubmissionRest>> GetSubmissionAsync(
            string email, string submissionId, [FromQuery]string contentFormat)
        {
            _logger.LogTrace("Retrieving submission {id} for {email}", submissionId, email);
            Submission result = await _context.Submissions.FirstOrDefaultAsync(
                s => s.UserEmail == email && s.Id == submissionId);
            if (result == null)
            {
                _logger.LogTrace("Submission not found");
                return NotFound();
            }
            try
            {
                string content;
                List<string> bloblPath = new() { email, submissionId };
                _logger.LogTrace("Found in db, retrieving blob");
                if (contentFormat == "url")
                {
                    _logger.LogTrace("Retrieving blob as sas url");
                    content = _storage.GetUrlBlob(bloblPath);
                }
                else
                {
                    _logger.LogTrace("Retrieving blob as binary data");
                    content = (await _storage.DownloadBlobAsync(bloblPath)).ToString();
                }
                _logger.LogTrace("Retrieved blob data successfuly");
                return Ok(new SubmissionRest(result, content));
            }
            catch(Exception e)
            {
                _logger.LogError("Error during blob retrieval {e}", e);
                return StatusCode(500);  // Internal error
            }
        }

        [HttpPost]
        public async Task<ActionResult<Submission>> Create([FromBody] SubmissionRest submissionData)
        {
            if (submissionData.UserEmail != StorageService.NormalizeFileName(submissionData.UserEmail))
            {
                _logger.LogWarning(
                    "Rejecting submission create, due to invalid email {email}", submissionData.UserEmail);
                return BadRequest();
            }
            _logger.LogTrace("Saving submission {submission}", submissionData);
            var submission = submissionData.GenerateSubmission();
            _context.Submissions.Add(submission);
            await _context.SaveChangesAsync();
            _logger.LogInformation("Submission saved to cosmos, now to blob");

            try
            {
                await _storage.UploadBlobAsync(
                    new List<string> { submission.UserEmail, submission.Id.ToString() },
                    new BinaryData(submissionData.Content)
                    );
                return Created("N/A", submission);
            }
            catch(Exception e)
            {
                // TODO: Test if this deletion really works
                _logger.LogWarning("Unable to save to blob, reverting db {e}", e);
                _context.Submissions.Remove(submission);
                await _context.SaveChangesAsync();
                // If there is exception, let it be some error
                _logger.LogTrace("Reverted  db succesfully");
                return StatusCode(500);
            }
        }




        // POST: SubmissionController/Delete/5
        private CosmosContext _context = null;
        private ILogger<SubmissionController> _logger = null;
        private StorageService _storage = null;
    }
}
