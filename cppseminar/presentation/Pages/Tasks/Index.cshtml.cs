using System;
using System.Linq;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Model;
using presentation.Services;
using Microsoft.AspNetCore.Mvc;
using System.Net.Mime;

namespace presentation.Pages.Tasks
{
    public class IndexModel : PageModel
    {
        private ILogger<IndexModel> _logger;
        private TaskService _taskService;
        private SubmissionService _submissionService;
        private IAuthorizationService _authService;
        public IList<TaskModel> TaskList = new List<TaskModel>();
        public bool IsAdmin = false;


        public IndexModel(ILogger<IndexModel> logger, TaskService taskService, SubmissionService submissionServicem, IAuthorizationService authService)
        {
            _logger = logger;
            _taskService = taskService;
            _submissionService = submissionServicem; 
            _authService = authService;
            
        }
        public async Task OnGetAsync()
        {
            try
            {
                IList<TaskModel> taskList = await _taskService.GetAllTasksAsync();
                var auth = await _authService.AuthorizeAsync(User, "Administrator");
                IsAdmin = auth.Succeeded;
                // Show only tasks for which you are authorized
                foreach (var task in taskList)
                {
                    if ((await _authService.AuthorizeAsync(
                        User, task, AuthorizationConstants.Submit)).Succeeded)
                    {
                        TaskList.Add(task);
                    }
                }
            }
            catch (Exception)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
            }
        }

        public async Task<ActionResult> OnGetDownloadAllAsync(string id)
        {
            try
            {
                var auth = await _authService.AuthorizeAsync(User, "Administrator");
                IsAdmin = auth.Succeeded;

                if (!IsAdmin)
                    return Page();

                var taskList = await _submissionService.DownloadTaskSubmissionsAsync(id);

                return File(taskList, MediaTypeNames.Application.Zip, $"{id}.zip");

            }
            catch (Exception)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
                return Page();
            }
        }
    }
}
