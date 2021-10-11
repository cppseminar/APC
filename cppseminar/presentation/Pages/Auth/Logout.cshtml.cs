using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Authentication;

namespace presentation.Pages.Auth
{
    public class LogoutModel : PageModel
    {
        public async Task<ActionResult> OnGetAsync()
        {
            await Request.HttpContext.SignOutAsync();
            return RedirectToPage("/Index");
        }
    }
}
