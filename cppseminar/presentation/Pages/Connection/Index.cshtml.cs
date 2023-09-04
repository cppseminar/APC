using System;
using System.Linq;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Filters;
using Microsoft.AspNetCore.Mvc;

namespace presentation.Pages.Connection
{
    [ServiceFilter(typeof(TestIPFilter))]
    public class IndexModel : PageModel
    {
        
        private ILogger<IndexModel> _logger;
        public bool IsAdmin = false;
    
        public IndexModel(ILogger<IndexModel> logger)
        {
            _logger = logger;
        }

        
        public async Task OnGetAsync(){
            _logger.LogInformation(Request.Headers["X-Forwarded-For"]); // this should be able to extract the original IP adress, after it goes through kubernetes
            var clientIPAddress = Request.HttpContext.Connection.RemoteIpAddress.ToString(); // extracting ip adress locally
            _logger.LogInformation($"Client IP address: {clientIPAddress}");
        }
    }
    
}
