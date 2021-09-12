using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Model;
using presentation.Services;

namespace presentation.Pages.Tasks
{
    public class DetailModel : PageModel
    {
        private ILogger<DetailModel> _logger;
        private TaskService _taskService;
        private IAuthorizationService _authService;
        private SubmissionService _submisssionService;

        public TaskModel TaskDetail { get; set; }
        [BindProperty]
        public Submission NewSubmission { get; set; }

        public DetailModel(ILogger<DetailModel> logger, TaskService taskService, IAuthorizationService authService, SubmissionService submissionService)
        {
            _logger = logger;
            _taskService = taskService;
            _authService = authService;
            _submisssionService = submissionService;
        }
        public async Task OnGetAsync(string id)
        {
            TaskDetail = await _taskService.GetTaskAsync(id);
            if (TaskDetail == null)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
            }
            var authenticated = await _authService.AuthorizeAsync(User, TaskDetail, AuthorizationConstants.Submit);
            if (!authenticated.Succeeded)
            {
                ModelState.AddModelError(string.Empty, "You are not authorized");
            }

        }

        public async Task<ActionResult> OnPostAsync(string id)
        {
            _logger.LogWarning("Processing submission POST");
            if (!ModelState.IsValid)
            {
                return Page();
            }
            TaskDetail = await _taskService.GetTaskAsync(id);
            if (TaskDetail == null)
            {
                _logger.LogWarning("Submission with invalid task {if}", id);
                return RedirectToPage("/");
            }
            var isAuthroized = await _authService.AuthorizeAsync(User, TaskDetail, AuthorizationConstants.Submit);
            if(!isAuthroized.Succeeded)
            {
                _logger.LogWarning("{user} tried submitting task {taskid} without permission", User, id);
                return Page();
            }
            if (TaskDetail.IsEnded())
            {
                ModelState.AddModelError(string.Empty, "Task deadline has passed");
                return Page();
            }
            Submission submission = Submission.GenerateSubmission(
                NewSubmission, TaskDetail, User.GetEmail());

            try
            {
                Submission result =
                    await _submisssionService.CreateSubmissionAsync(submission);
                return RedirectToPage("/Submissions/Index");
            }
            catch (OperationFailedException)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
            }
            return Page();
            


        }
    }
}
