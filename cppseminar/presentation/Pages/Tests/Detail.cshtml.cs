using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Model;
using presentation.Services;

namespace presentation.Pages.Tests
{
    public class DetailModel : PageModel
    {
        private ILogger<DetailModel> _logger;
        private TestService _testService;
        public TestRun TestRunResult;

        public DetailModel(ILogger<DetailModel> logger, TestService testService)
        {
            _logger = logger;
            _testService = testService;
        }
        public async Task OnGetAsync(Guid guid)
        {
            try
            {
                TestRunResult = await _testService.GetOneTest(User.GetEmail(), guid);
            }
            catch(Exception)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
            }
        }
    }
}
