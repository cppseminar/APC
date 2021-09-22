using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Model;
using presentation.Services;

// TODO: Enforce GUID on TASKs also

namespace presentation.Pages.Submissions
{
    public class DetailModel : PageModel
    {
        private ILogger<DetailModel> _logger;
        private SubmissionService _submissionService;
        public Submission MySubmission { get; set; }

        public DetailModel(ILogger<DetailModel> logger, SubmissionService submissionService)
        {
            _logger = logger;
            _submissionService = submissionService;
        }

        public async Task OnGetAsync([Required]Guid id)
        {
            if (!ModelState.IsValid)
            {
                return;
            }

            try
            {
                MySubmission =
                    await _submissionService.GetSubmissionAsync(User.GetEmail(), id.ToString());
            }
            catch(Exception)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
            }


        }
    }
}
