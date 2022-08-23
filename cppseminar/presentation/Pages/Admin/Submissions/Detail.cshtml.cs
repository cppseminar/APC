using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using presentation.Model;
using presentation.Services;

namespace presentation.Pages.Admin.Submissions
{
    public class DetailModel : PageModel
    {
        private readonly SubmissionService _submissionService;
        private readonly TestCaseService _testCaseService;
        private readonly TestService _testService;

        [BindProperty]
        public string TestGuid { get; set; }

        public Submission CurrentSubmission { get; set; }
        public List<TestCaseRest> TestCaseList { get; set; }

        public DetailModel(
            SubmissionService submissionService,
            TestCaseService testCaseService,
            TestService testService)
        {
            _submissionService = submissionService;
            _testCaseService = testCaseService;
            _testService = testService;
        }

        public async Task OnGetAsync(
            [FromRoute][Required]string user,
            [FromRoute][Required]string submissionId)
        {
            try
            {
                CurrentSubmission = await _submissionService.GetSubmissionAsync(
                    user, submissionId.ToString(), urlOnly: false);

                TestCaseList = await _testCaseService.GetByTask(CurrentSubmission.TaskId);
            }
            catch(Exception)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
            }
        }

        public async Task<ActionResult> OnPostAsync(
            [FromRoute][Required] string user,
            [FromRoute][Required] string submissionId)
        {
            if (!ModelState.IsValid)
            {
                return Page();
            }

            var testCase = await _testCaseService.GetById(TestGuid);
            var submission = await _submissionService.GetSubmissionAsync(
                user, submissionId.ToString(), urlOnly: true);

            if (submission == null)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
                return Page();
            }

            TestRequestRest testRequest = new()
            {
                ContentUrl = submission.Content,
                CreatedBy = User.GetEmail(),
                SubmissionId = submission.Id,
                TaskId = submission.TaskId,
                TaskName = submission.TaskName,
                TestCaseId = testCase.Id,
                TestCaseName = testCase.Name,
                Counted = !User.IsAdmin()
            };
            try
            {
                if (await _testService.CreateTest(testRequest))
                {
                    return RedirectToAction("OnGetAsync");
                }
                else
                {
                    ModelState.AddModelError(string.Empty, "You reached limit for max test runs");
                    return RedirectToPage("/Tests/Limit");
                }
            }
            catch (Exception)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
                return Page();
            }

            // TODO: Check task date

            // Check permissions on submission and task and test case
        }
    }
}
