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
        public bool IsAdmin = false;

        public DetailModel(ILogger<DetailModel> logger, TaskService taskService, IAuthorizationService authService, SubmissionService submissionService)
        {
            _logger = logger;
            _taskService = taskService;
            _authService = authService;
            _submisssionService = submissionService;
        }

        public async Task OnGetAsync(string id)
        {
            _logger.LogTrace("Request to show task details");
            IsAdmin = (await _authService.AuthorizeAsync(User, "Administrator")).Succeeded;
            TaskModel retrievedTask = await _taskService.GetTaskAsync(id);
            if (retrievedTask == null)
            {
                _logger.LogTrace("Task retieval from database failed");
                ModelState.AddModelError(string.Empty, "Operation failed");
            }
            var authenticated = await _authService.AuthorizeAsync(User, retrievedTask, AuthorizationConstants.Submit);
            if (!authenticated.Succeeded)
            {
                _logger.LogWarning("User {user} tried accessing unauthorized task {task}", User, id);
                ModelState.AddModelError(string.Empty, "You are not authorized");
            }
            else
            {
                TaskDetail = retrievedTask;
            }
        }

        public async Task<ActionResult> OnPostAsync(string id)
        {
            if (!ModelState.IsValid)
            {
                return Page();
            }
            _logger.LogTrace("Processing submission form POST");
            TaskModel retrievedTask = await _taskService.GetTaskAsync(id);
            if (retrievedTask == null)
            {
                _logger.LogWarning("Submission with invalid task {id}", id);
                return RedirectToPage("/Tasks/Index");
            }
            var isAuthroized = await _authService.AuthorizeAsync(User, retrievedTask, AuthorizationConstants.Submit);
            if(!isAuthroized.Succeeded)
            {
                _logger.LogWarning("{user} tried submitting task {taskid} without authorization", User.GetEmail(), id);
                return RedirectToPage("/Tasks/Index");
            }
            TaskDetail = retrievedTask; // Now it's ok to show user this task
            if (TaskDetail.IsEnded() && !User.IsAdmin())
            {
                _logger.LogTrace("Submission is after deadline passed {deadline}", TaskDetail.Ends);
                ModelState.AddModelError(string.Empty, "Task deadline has passed");
                return Page();
            }
            Submission submission = Submission.GenerateSubmission(
                NewSubmission, TaskDetail, User.GetEmail());

            try
            {
                _logger.LogTrace("Submission passed tests, gonna send to service");
                Submission _ =
                    await _submisssionService.CreateSubmissionAsync(submission);
                _logger.LogTrace("Submission was created successfuly");
                return RedirectToPage("/Submissions/Success");
            }
            catch (Exception e)
            {
                _logger.LogWarning("Submission failed with error {e}", e);
                ModelState.AddModelError(string.Empty, "Operation failed");
            }
            return Page();
        }
    }
}
