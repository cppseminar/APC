using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
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
        // GET: SubmissionController
        public IEnumerable<Submission> Index()
        {
            return _context.Submissions;
        }

        // https://www.yogihosting.com/aspnet-core-api-controllers/

        [HttpPost]
        public async Task<ActionResult<Submission>> Create([FromBody] SubmissionRest submissionData)
        {
            _logger.LogTrace("Saving this {submission}", submissionData);
            var submission = submissionData.GenerateSubmission();
            _context.Submissions.Add(submission);
            _context.SaveChanges();
            _logger.LogInformation("Saved submission");
            await _storage.UploadBlobAsync(new List<string> { "foldrik", submission.Id.ToString() }, new BinaryData(submissionData.Content));

            return submission;
        }


        // POST: SubmissionController/Delete/5
        private CosmosContext _context = null;
        private ILogger<SubmissionController> _logger = null;
        private StorageService _storage = null;
    }
}
