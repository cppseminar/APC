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
    }
}
