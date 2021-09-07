using System;
using System.Collections.Generic;
using System.Threading.Tasks;
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
        public IList<TaskModel> TaskList = new List<TaskModel>();


        public IndexModel(ILogger<IndexModel> logger, TaskService service)
        {
            _logger = logger;
            _service = service;
        }
        public async Task OnGetAsync()
        {
            try
            {
                TaskList = await _service.GetAllTasksAsync();
            }
            catch (Exception)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
            }


        }
    }
}
