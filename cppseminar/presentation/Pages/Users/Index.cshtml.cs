using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Model;
using presentation.Services;

namespace presentation.Pages.Users
{
    [Authorize("Administrator")]
    public class IndexModel : PageModel
    {
        private ILogger<IndexModel> _logger;
        private AuthenticationService _authService;
        public IEnumerable<string> AllUsers = Enumerable.Empty<string>();
        public IDictionary<string, string> Claims { get; set; }

        public IndexModel(ILogger<IndexModel> logger, AuthenticationService authService)
        {
            _logger = logger;
            _authService = authService;
        }
        public async Task OnGetAsync()
        {
            try
            {
                _logger.LogTrace("Obtaining list of users for admin");
                AllUsers = await _authService.GetAllUsers();
                _logger.LogTrace("List successfuly retrieved");
            }
            catch(Exception e)
            {
                _logger.LogWarning("Error during obtaining all users {e}", e);
                ModelState.AddModelError(string.Empty, "Operation failed. Check log");
            }
        }

        public async Task OnGetDetail([FromQuery][Required]string email)
        {
            if (!ModelState.IsValid)
            {
                return;
            }

            try
            {
                // TODO: Maybe validation of email
                _logger.LogTrace("Admin obtaining details for user {email}", email);
                Claims = await _authService.GetUserClaimsAsync(email);
                _logger.LogTrace("Claims retrieved successfuly");
            }
            catch (Exception e)
            {
                ModelState.AddModelError(string.Empty, "Obtaining details failed :/");
                _logger.LogWarning("Get user details failed {e}", e);
            }
        }

    }
}
