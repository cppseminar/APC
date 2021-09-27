using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
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

        public Submission MySubmission { get; set; }
        public List<TestCaseRest> TestCaseList { get; set; }

        public DetailModel(ILogger<DetailModel> logger,
                           SubmissionService submissionService,
                           TestCaseService testCaseService,
                           IAuthorizationService authService)
        {
            _logger = logger;
            _submissionService = submissionService;
            _testCaseService = testCaseService;
            _authService = authService;
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
    }
}
