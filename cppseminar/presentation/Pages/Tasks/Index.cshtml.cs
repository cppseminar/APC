using System;
using System.Linq;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Model;
using presentation.Services;

namespace presentation.Pages.Tasks
{
    public class IndexModel : PageModel
    {
        private ILogger<IndexModel> _logger;
        private TaskService _service;
        private IAuthorizationService _authService;
        public IList<TaskModel> TaskList = new List<TaskModel>();
        public bool IsAdmin = false;


        public IndexModel(ILogger<IndexModel> logger, TaskService service, IAuthorizationService authService)
        {
            _logger = logger;
            _service = service;
            _authService = authService;
            
        }
        public async Task OnGetAsync()
        {
            try
            {
                IList<TaskModel> taskList = await _service.GetAllTasksAsync();
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
    }
}
