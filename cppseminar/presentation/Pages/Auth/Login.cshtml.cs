using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace presentation.Pages.Auth
{
    public class LoginModel : PageModel
    {
        public ActionResult OnGet()
        {
            return RedirectToPage("/Index");
        }
    }
}
