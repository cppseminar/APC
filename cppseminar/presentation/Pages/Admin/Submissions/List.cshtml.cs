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

namespace presentation.Pages.Admin.Submissions
{
    public class ListModel : PageModel
    {
        public ListModel(ILogger<ListModel> logger, SubmissionService submissionService, AuthenticationService authService)
        {
            _logger = logger;
            _submissionService = submissionService;
            _authService = authService;
        }

        public async Task OnGetAsync()
        {            
            try
            {
                if (SelectedUser == "")
                    Submissions = await _submissionService.GetSubmissionsAsync();
                else
                    Submissions = await _submissionService.GetUserSubmissionsAsync(SelectedUser);
            // paging
            numberOfPages = (int)Math.Ceiling(Convert.ToDouble(Submissions.Count()) / Convert.ToDouble(pageSize));
            int startIndex = PageNumber*pageSize;
            DisplayedSubmissions = Submissions.Skip(startIndex).Take(pageSize);
            }
            catch (OperationFailedException e)
            {
                _logger.LogError("Cannot retrieve submissions {user}. {e}", SelectedUser, e);

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
                _logger.LogError("Cannot retrieve all user set. {e}", e);

                ModelState.AddModelError(string.Empty, e.Message);
            }
        }

        [BindProperty(SupportsGet = true)]
        public string SelectedUser { get; set; }

        public IEnumerable<Submission> Submissions = Enumerable.Empty<Submission>();

        public List<SelectListItem> Users = null;
        public IEnumerable<Submission> DisplayedSubmissions = Enumerable.Empty<Submission>();
         [BindProperty(SupportsGet = true)]
        public int PageNumber { get; set; }
        public int pageSize = 10;
        public int numberOfPages = 0;

        private readonly ILogger<ListModel> _logger = null;
        private readonly SubmissionService _submissionService = null;
        private readonly AuthenticationService _authService = null;
    }
}
