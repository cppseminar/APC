using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Model;
using presentation.Services;

namespace presentation.Pages.Admin.TestCase
{
    public class CreateModel : PageModel
    {
        private ILogger<CreateModel> _logger;
        private TestCaseService _testCaseService;

        [BindProperty]
        public TestCaseRest  NewCase { get; set; }

        public CreateModel(ILogger<CreateModel> logger, TestCaseService testCaseService)
        {
            _logger = logger;
            _testCaseService = testCaseService;
        }

        public void OnGet()
        {

        }

        public async Task<ActionResult> OnPostAsync()
        {
            if (!ModelState.IsValid)
            {
                return Page();
            }
            NewCase.CreatedBy = User.GetEmail();
            try
            {
                await _testCaseService.CreateCase(NewCase);
                return RedirectToPage("/TestCase/Index");
            }
            catch(Exception e)
            {
                _logger.LogTrace("Test case creation error {e}", e);
                ModelState.AddModelError(string.Empty, "Operation failed");
            }
            return Page();
        }
    }
}
