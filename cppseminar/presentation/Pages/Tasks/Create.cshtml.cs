using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Model;
using presentation.Services;

namespace presentation.Pages.Tasks
{
    // TODO: Require sign in
    // TODO: Require claim
    [Authorize(Policy = "Administrator")]
    public class CreateModel : PageModel
    {
        public CreateModel(ILogger<CreateModel> logger, TaskService taskService)
        {
            _logger = logger;
            _taskService = taskService;
        }
        public void OnGet()
        {
        }

        public async Task<ActionResult> OnPostAsync()
        {
            _logger.LogTrace("TaskModel {TaskModel} submitted", NewTask);
            if (!ModelState.IsValid)
            {
                _logger.LogTrace("Submitted TaskModel is invalid {errors}", ModelState.Values);
                return Page();

            }
            else
            {
                var email = HttpContext.User.Claims.First(claim => claim.Type == ClaimTypes.Email);
                if (email == null)
                {
                    ModelState.AddModelError(string.Empty, "Please sign in again");
                    return Page();
                }
                NewTask.CreatedBy = email.Value;
                bool result = await _taskService.CreateTaskAsync(NewTask);
                if (result)
                {
                    return RedirectToPage("/Tasks/Index");
                }
                else
                {
                    ModelState.AddModelError(string.Empty, "Submission failed. Please try again later");
                    return Page();
                }

            }

        }

        [BindProperty]
        public TaskModel NewTask { get; set; }
        private TaskService _taskService = null;
        private ILogger<CreateModel> _logger = null;
    }
}
