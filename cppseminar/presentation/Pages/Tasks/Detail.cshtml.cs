using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
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
        private TaskService _service;
        public TaskModel TaskDetail { get; set; }

        public DetailModel(ILogger<DetailModel> logger, TaskService service)
        {
            _logger = logger;
            _service = service;
        }
        public async Task OnGetAsync(string id)
        {
            TaskDetail = await _service.GetTaskAsync(id);
            if (TaskDetail == null)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
            }
        }
    }
}
