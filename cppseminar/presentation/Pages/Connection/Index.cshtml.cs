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
        public string upper;
        public string lower;
    
        public IndexModel(ILogger<IndexModel> logger, List<string> allowedIpAddresses)
        {
            _logger = logger;
            this.upper = allowedIpAddresses[0]; // we wont be able to use this in testipfilter cuz it needs to be static or constant... we dont have the information 
            this.lower = allowedIpAddresses[1];
        }

        
        public async Task OnGetAsync(){
            _logger.LogInformation(Request.Headers["X-Forwarded-For"]); // this should be able to extract the original IP adress, after it goes through kubernetes
            var clientIPAddress = Request.HttpContext.Connection.RemoteIpAddress.ToString(); // extracting ip adress locally
            _logger.LogInformation($"Client IP address: {clientIPAddress}");
        }
    }
    
}
