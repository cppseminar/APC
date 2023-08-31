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
    [TestIPFilter("172.24.0.1")]
    public class IndexModel : PageModel
    {
        private ILogger<IndexModel> _logger;
        public bool IsAdmin = false;
        public string upper;
        public string lower;
        public IndexModel(List<string> allowedIpAddresses) {
            this.upper = allowedIpAddresses[0];
            this.lower = allowedIpAddresses[1];
        }
        public async Task OnGetAsync(){
            System.Console.WriteLine(Request.Headers["X-Forwarded-For"]); // this should be able to extract the original IP adress, after it goes through kubernetes
            var clientIPAdress = Request.HttpContext.Connection.RemoteIpAddress.ToString(); // extracting ip adress locally
            System.Console.WriteLine(clientIPAdress);
        }
    }
    
}
