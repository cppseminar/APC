using System;
using System.Linq;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Model;
using presentation.Services;
using System.Net.Mime;
using Microsoft.AspNetCore.Mvc;


namespace presentation.Pages.Monitoring
{
    public class IndexModel : PageModel
    {
        private ILogger<IndexModel> _logger = null;
        [BindProperty]
        public List<ConnectionLog> LoggedUsers{get;set;}
        private readonly MonitoringService _monitoringService = null;

        public IndexModel(ILogger<IndexModel> logger, MonitoringService monitoringService)
        {
            _logger = logger;
            _monitoringService = monitoringService;
        }

        public async Task OnGetAsync()
        {
            try
            {
                _logger.LogTrace("Obtaining list of monitored users for admin");
                _logger.LogTrace("List successfuly retrieved");

            }
            catch(Exception e)
            {
                _logger.LogWarning("Error during logged users {e}", e);
                ModelState.AddModelError(string.Empty, "Operation failed. Check log");
            }
        }
        
        
    }
}
