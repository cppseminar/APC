using System;
using System.ComponentModel.DataAnnotations;
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

        [BindProperty]
        public bool Counted { get; set; } = true;

        public DetailModel(TestService testService)
        {
            _testService = testService;
        }

        public async Task OnGetAsync(string userEmail, [Required]string testId)
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

        public async Task<ActionResult> OnPostCountedAsync([Required]string userEmail, [Required] string testId)
        {
            await _testService.SetCounted(
                userEmail: userEmail,
                testRunId: testId,
                value: Counted);
            return RedirectToAction("Index");
        }
    }
}
