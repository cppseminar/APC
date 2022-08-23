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
        private readonly ILogger<DetailModel> _logger;
        private readonly TestService _testService;

        public TestRun TestRunResult;

        public DetailModel(ILogger<DetailModel> logger, TestService testService)
        {
            _logger = logger;
            _testService = testService;
        }

        public async Task OnGetAsync(string id)
        {
            try
            {
                TestRunResult = await _testService.GetOneTest(User.GetEmail(), id);
            }
            catch (Exception e)
            {
                _logger.LogError("Cannot get test details {e}", e);

                ModelState.AddModelError(string.Empty, "Operation failed");
            }
        }
    }
}
