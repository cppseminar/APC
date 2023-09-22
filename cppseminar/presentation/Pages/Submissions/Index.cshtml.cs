using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Model;
using presentation.Services;


using System.ComponentModel;
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
                Submissions = await _submissionService.GetUserSubmissionsAsync(User.GetEmail(), PageNumber);
                numberOfPages = await _submissionService.GetNumberOfPages(User.GetEmail()); 
            }
            catch(OperationFailedException e)
            {
                ModelState.AddModelError(string.Empty, e.Message);
            }
        }

        [BindProperty]
        public Submission MySubmission { get; set; }
        public IList<string> Errors = new List<string>();
        public IEnumerable<Submission> Submissions = Enumerable.Empty<Submission>();
        public IEnumerable<Submission> DisplayedSubmissions = Enumerable.Empty<Submission>();
        [BindProperty(SupportsGet = true)]
        public int PageNumber { get; set; }
        public int numberOfPages = 0;

        private ILogger<IndexModel> _logger = null;
        private SubmissionService _submissionService = null;

    }
}
