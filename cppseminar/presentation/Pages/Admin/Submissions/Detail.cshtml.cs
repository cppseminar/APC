using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using presentation.Model;
using presentation.Services;

namespace presentation.Pages.Admin.Submissions
{
    public class DetailModel : PageModel
    {
        private SubmissionService _submissionService;

        public Submission CurrentSubmission { get; set; }

        public DetailModel(SubmissionService submissionService)
        {
            _submissionService = submissionService;
        }

        public async Task OnGetAsync(
            [FromRoute][Required]string user,
            [FromRoute][Required]Guid submissionId)
        {
            try
            {
                CurrentSubmission = await _submissionService.GetSubmissionAsync(
                    user, submissionId.ToString(), urlOnly: false);
            }
            catch(Exception e)
            {
                ModelState.AddModelError(string.Empty, "Operation failed");
            }
        }
    }
}
