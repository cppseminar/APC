using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.AspNetCore.Mvc.Rendering;
using Microsoft.Extensions.Logging;
using presentation.Model;
using presentation.Services;

namespace presentation.Pages.Submissions
{
    public class AllModel : PageModel
    {
        public AllModel(ILogger<AllModel> logger, SubmissionService submissionService, AuthenticationService authService)
        {
            _logger = logger;
            _submissionService = submissionService;
            _authService = authService;
        }

        public async Task OnGetAsync()
        {            
            Console.WriteLine(SelectedUser);
            try
            {
                if (SelectedUser == "")
                    Submissions = await _submissionService.GetSubmissionsAsync();
                else
                    Submissions = await _submissionService.GetUserSubmissionsAsync(SelectedUser);
            }
            catch (OperationFailedException e)
            {
                ModelState.AddModelError(string.Empty, e.Message);
            }

            try
            {
                Users = (await _authService.GetAllUsers()).Select(
                    x => new SelectListItem(x, x)
                ).ToList();

                Users.Add(new SelectListItem("<all>", "", true));
            }
            catch (Exception e)
            {
                ModelState.AddModelError(string.Empty, e.Message);
            }
        }

        [BindProperty(SupportsGet = true)]
        public string SelectedUser { get; set; }

        public IEnumerable<Submission> Submissions = Enumerable.Empty<Submission>();

        public List<SelectListItem> Users = null;


        private ILogger<AllModel> _logger = null;
        private SubmissionService _submissionService = null;
        private AuthenticationService _authService = null;
    }
}
