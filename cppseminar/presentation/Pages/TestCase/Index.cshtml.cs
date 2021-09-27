using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using presentation.Model;
using presentation.Services;

namespace presentation.Pages.TestCase
{
    [Authorize("Administrator")]
    public class IndexModel : PageModel
    {
        private TestCaseService _testCaseService;

        public List<TestCaseRest> Cases { get; set; }

        public IndexModel(TestCaseService testCaseService)
        {
            _testCaseService = testCaseService;
        }
        public async Task OnGetAsync()
        {
            Cases = await _testCaseService.GetAll();
            if (Cases == null) // Error
            {
                ModelState.AddModelError(string.Empty, "Failed loading data");
            }
        }
    }
}
