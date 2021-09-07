using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Model;
using presentation.Services;

namespace presentation.Pages.Submissions
{
    public class IndexModel : PageModel
    {
        public IndexModel(ILogger<IndexModel> logger, SubmissionService submissionService)
        {
            _logger = logger;
            _submissionService = submissionService;
        }

        public async Task OnGetAsync()
        {
            try
            {
                Submissions = await _submissionService.GetSubmissionsAsync();
            }
            catch(OperationFailedException e)
            {
                ModelState.AddModelError(string.Empty, e.Message);
            }
            
        }

        public async Task<IActionResult> OnPostAsync()
        {
            if (!ModelState.IsValid)
            {
                Console.WriteLine("Invalid post");
                return Page();
            }
            try
            {
                Submission newSubmission = this.MySubmission;
                // Let's add rest of the fields
                newSubmission.UserEmail = "fake@email.com";
                newSubmission.TaskId = "1234";
                var result = await _submissionService.CreateSubmissionAsync(this.MySubmission);
                return RedirectToPage("./Success");
            }
            catch (OperationFailedException e)
            {
                Errors.Add(e.Message);
            }
            return Page();
        }


        [BindProperty]
        public Submission MySubmission { get; set; }
        public IList<string> Errors = new List<string>();
        public IEnumerable<Submission> Submissions = Enumerable.Empty<Submission>();

        private ILogger<IndexModel> _logger = null;
        private SubmissionService _submissionService = null;

    }
}
