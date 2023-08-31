using System;
using System.Linq;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Filters;

namespace presentation.Pages.Connection
{
    public class IndexModel : PageModel
    {
        [TestIPFilter("172.18.0.0", "172.18.255.255")]
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
