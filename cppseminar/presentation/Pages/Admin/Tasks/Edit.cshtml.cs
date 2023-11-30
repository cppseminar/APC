using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Model;
using presentation.Services;
using System;
using System.Threading.Tasks;

namespace presentation.Pages.Tasks
{
    [Authorize(Policy = "Administrator")]
    public class EditModel : PageModel
    {
        private ILogger<EditModel> _logger;
        private TaskService _taskService;

        [BindProperty]
        public TaskModel MyTask { get; set; }

        public EditModel(ILogger<EditModel> logger, TaskService taskService)
        {
            _logger = logger;
            _taskService = taskService;
        }


        public async Task OnGetAsync([Bind]string taskId)
        {
            MyTask = await _taskService.GetTaskAsync(taskId);
        }

        public async Task<ActionResult> OnPostAsync([Bind] string taskId)
        {
            if (!ModelState.IsValid)
            {
                return Page();
            }

            try
            {
                await _taskService.PatchOneAsync(taskId, MyTask);

            }
            catch(Exception ex)
            {
                ModelState.AddModelError("Error", ex.Message);
                return Page();
            }

            return RedirectToPage("/Tasks/Index");
        }

    }
}
