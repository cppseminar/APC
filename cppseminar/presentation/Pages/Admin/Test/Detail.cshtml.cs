using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using presentation.Model;
using presentation.Services;

namespace presentation.Pages.Admin.Test
{
    public class DetailModel : PageModel
    {
        private TestService _testService;

        public TestRun TestResult { get; set; }

        public DetailModel(TestService testService)
        {
            _testService = testService;
        }
        public async Task OnGetAsync(string userEmail, [Required]Guid testId)
        {
            try
            {
                TestResult = await _testService.GetOneTest(userEmail, testId);
            }
            catch(Exception)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
            }
        }
    }
}
