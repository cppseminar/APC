using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using Polly;
using Polly.Retry;
using presentation.Model;
using presentation.Services;

// TODO: Enforce GUID on TASKs also

namespace presentation.Pages.Submissions
{
    public class DetailModel : PageModel
    {
        private ILogger<DetailModel> _logger;
        private SubmissionService _submissionService;
        private TestCaseService _testCaseService;
        private IAuthorizationService _authService;
        private TestService _testService;

        public Submission MySubmission { get; set; }
        public List<TestCaseRest> TestCaseList { get; set; }
        [BindProperty]
        public Guid TestGuid { get; set; }

        public DetailModel(ILogger<DetailModel> logger,
                           SubmissionService submissionService,
                           TestCaseService testCaseService,
                           IAuthorizationService authService,
                           TestService testService)
        {
            _logger = logger;
            _submissionService = submissionService;
            _testCaseService = testCaseService;
            _authService = authService;
            _testService = testService;
        }

        public async Task OnGetAsync([Required]Guid id)
        {
            if (!ModelState.IsValid)
            {
                return;
            }

            try
            {
                MySubmission =
                    await _submissionService.GetSubmissionAsync(User.GetEmail(), id.ToString());
                var allCases = await _testCaseService.GetByTask(MySubmission.TaskId);
                TestCaseList = new List<TestCaseRest>();
                foreach (var oneCase in allCases)
                {
                    if ((await _authService.AuthorizeAsync(
                        User, oneCase, AuthorizationConstants.Submit)).Succeeded)
                    {
                        TestCaseList.Add(oneCase);
                    }
                }
            }
            catch(Exception)
            {
                ModelState.AddModelError(string.Empty, "Failed loading some data");
            }
        }

        public async Task<ActionResult> OnPostAsync([Required][FromRoute] Guid id)
        {
            if (!ModelState.IsValid)
            {
                return Page();
            }

            var testCase = await _testCaseService.GetById(TestGuid);
            if (testCase == null ||
                !(await _authService.AuthorizeAsync(User, testCase, AuthorizationConstants.Submit)).Succeeded)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
            }

            var submission = await _submissionService.GetSubmissionAsync(
                User.GetEmail(), id.ToString(), urlOnly: true);

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
                TestCaseName = testCase.Name
            };
            try
            {
                await _testService.CreateTest(testRequest);
                return RedirectToPage("/Index");
            }
            catch(Exception)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
                return Page();
            }

            // TODO: Check task date

            // Check permissions on submission and task and test case
        }
    }
}
