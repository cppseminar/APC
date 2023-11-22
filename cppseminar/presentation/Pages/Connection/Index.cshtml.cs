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
    [ServiceFilter(typeof(PageIPFilter))]
    public class IndexModel : PageModel
    {
        
        private ILogger<IndexModel> _logger;
        public bool IsAdmin = false;
    
        public IndexModel(ILogger<IndexModel> logger)
        {
            _logger = logger;
        }
    }
}
