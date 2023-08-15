using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using presentation.Model;
using presentation.Services;

namespace presentation.Pages.Admin.TestCase
{
    public class EditModel : PageModel
    {
        private TestCaseService _testCaseService;

        [BindProperty]
        public TestCaseRest TestCase { get; set; }

        private string testCaseId;

        public EditModel(TestCaseService testCaseService)
        {
            _testCaseService = testCaseService;
        }
        public async Task OnGetAsync([FromQuery] string caseId)
        {
            System.Console.WriteLine("test case  id" + caseId);
            TestCase = await _testCaseService.GetById(caseId);
            System.Console.WriteLine("Test case id " + TestCase.Id);
            if (TestCase == null) // Error
            {
                ModelState.AddModelError(string.Empty, "Failed loading data");
            }
        }
        public async Task OnPostAsync([FromQuery] string caseId){ 
            if (!ModelState.IsValid){
                ModelState.AddModelError(string.Empty, "Model is not valid");
            }
            try{
                System.Console.WriteLine(TestCase.Id); // http post resets fields not in form and it ignores bindnever attribute
                System.Console.WriteLine(TestCase.MaxRuns);
                await _testCaseService.UpdateTest(caseId, TestCase);
            }
            catch (Exception){
                ModelState.AddModelError(string.Empty, "Failed updating test case");
            }
        }
    }
}
