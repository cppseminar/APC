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
                
                // if (SelectedUser == "")
                // Submissions = await _submissionService.GetSubmissionsAsync();
                // else
                System.Console.WriteLine("Page "+ PageNumber + "Selected user "+ SelectedUser);
                Submissions = await _submissionService.GetUserSubmissionsAsync(SelectedUser, PageNumber);
                
                // Paging
               if (numberOfPages == -1 || (PreviouslySelectedUser != null && PreviouslySelectedUser != SelectedUser)){
                    System.Console.WriteLine("Idem zistovat counts");
                    var counts = await _submissionService.GetCounts(SelectedUser); 
                    System.Console.WriteLine(counts[0]);
                    numberOfPages = counts[1];
                    System.Console.WriteLine("Number of pages "+ numberOfPages);
                }
                
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
            PreviouslySelectedUser = SelectedUser;
        }

        [BindProperty(SupportsGet = true)]
        public string SelectedUser { get; set; }

        public IEnumerable<Submission> Submissions = Enumerable.Empty<Submission>();

        public List<SelectListItem> Users = null;
        
         [BindProperty(SupportsGet = true)]
        public int PageNumber { get; set; }
        public int PageSize = 10;
        public long numberOfPages = -1;

        private readonly ILogger<ListModel> _logger = null;
        private readonly SubmissionService _submissionService = null;
        private readonly AuthenticationService _authService = null;
        private string PreviouslySelectedUser = null;
    }
}
