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

namespace presentation.Pages.Connection
{
    public class IndexModel : PageModel
    {
        private ILogger<IndexModel> _logger;
        public bool IsAdmin = false;
        public async Task OnGetAsync(){
            System.Console.WriteLine(Request.Headers["X-Forwarded-For"]); // this should be able to extract the original IP adress, after it goes through kubernetes
            var clientIPAdress = Request.HttpContext.Connection.RemoteIpAddress.ToString(); // extracting ip adress locally
            System.Console.WriteLine(clientIPAdress);
        
        }
    }
    
}
