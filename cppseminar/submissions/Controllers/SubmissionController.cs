using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using submissions.Data;
using submissions.Models;

namespace submissions.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class SubmissionController : Controller
    {
        public SubmissionController(SubmissionContext context, ILogger<SubmissionController> logger)
        {
            _context = context;
            _logger = logger;
        }

        [HttpGet]
        // GET: SubmissionController
        public IEnumerable<Submission> Index()
        {
            return _context.Submissions;
        }

        // https://www.yogihosting.com/aspnet-core-api-controllers/

        [HttpPost]
        public ActionResult<Submission> Create([FromBody] SubmissionRest submissionData)
        {
            _logger.LogInformation("Saving this {submission}", submissionData);
            var submission = submissionData.GenerateSubmission();



            _context.Database.EnsureCreated();
            //_context.Submissions.Count();
            //_logger.LogInformation("Going to save {submission}", submission);
            _context.Submissions.Add(submission);
            _context.SaveChanges();
            _logger.LogInformation("Saved submission");

            return submission;
        }


        // POST: SubmissionController/Delete/5
        private SubmissionContext _context = null;
        private ILogger<SubmissionController> _logger = null;
    }
}
