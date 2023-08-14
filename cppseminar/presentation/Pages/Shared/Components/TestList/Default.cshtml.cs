using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using presentation.Model;
using presentation.Services;
namespace presentation.Pages.Shared.Components.TestList
{
    public class TestListViewComponent : ViewComponent
    {
        private ILogger<TestListViewComponent> _logger;
        private TestService _testService;

        [BindProperty]
        public bool Counted {get; set; }

        public TestListViewComponent(ILogger<TestListViewComponent> logger, TestService testService)
        {
            _logger = logger;
            _testService = testService;
        }
        public async Task<IViewComponentResult> InvokeAsync(
            string userEmail,
            string submissionId,
            bool isAdmin = false, bool counted = false)
        {
            var items = await _testService.GetTestsAsync(userEmail, submissionId); // returns all test runs for current submission
            ViewData["IsAdmin"] = isAdmin;

            return View(items); // this was items
        }
        // public async Task<ActionResult> OnPostCountedAsync()
        // {
        //     System.Console.WriteLine("Som vo vnutornom poste");
        //     return null;
        // }
    }
}
