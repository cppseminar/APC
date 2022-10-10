using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.RazorPages;
using System;

namespace presentation.Pages
{
    [AllowAnonymous]
    public class IndexModel : PageModel
    {
        public string DocsLink = Environment.GetEnvironmentVariable("LINKS_CURRENT_DOCS");
    }
}
