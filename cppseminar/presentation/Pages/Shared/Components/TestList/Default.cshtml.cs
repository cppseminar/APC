using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using presentation.Services;
namespace presentation.Pages.Shared.Components.TestList
{
    public class TestListViewComponent : ViewComponent
    {
        private ILogger<TestListViewComponent> _logger;
        private TestService _testService;

        public TestListViewComponent(ILogger<TestListViewComponent> logger, TestService testService)
        {
            _logger = logger;
            _testService = testService;
        }
        public async Task<IViewComponentResult> InvokeAsync(
            string userEmail,
            string taskId,
            string submissionId)
        {
            if (submissionId == string.Empty)
            {
                submissionId = null;
            }

            if (userEmail != null)
            {
                var items = await _testService.GetTestsForUserAsync(userEmail, submissionId);
                return View(items);

            }
            else
            {
                throw new Exception("Not implemented");
            }
        }
    }
}
