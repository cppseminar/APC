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

namespace presentation.Pages.Admin.Users
{
    [Authorize("Administrator")]
    public class IndexModel : PageModel
    {
        private ILogger<IndexModel> _logger;
        private AuthenticationService _authService;

        public IEnumerable<string> AllUsers = Enumerable.Empty<string>();
        public IDictionary<string, string> Claims { get; set; }

        [BindProperty]
        public string studentlist { get; set; }
        [BindProperty]
        public string claimname { get; set; }

        [BindProperty]
        public string claimvalue { get; set; }


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

        public async Task<IActionResult> OnPost()
        {
            foreach (KeyValuePair<string, string> entry in
                     new Dictionary<string, string> { { "claimname", "Claim name" },
                                                      { "claimvalue", "Claim value" },
                                                      { "studentlist", "Student list" }})
            {
                if (string.IsNullOrWhiteSpace(Request.Form[entry.Key].ToString()))
                {
                    string errmsg = string.Format("{0} cannot be empty.", entry.Value);
                    _logger.LogTrace(errmsg);
                    ModelState.AddModelError(string.Empty, errmsg);
                    return Page();
                }
            }

            List<UserRest> studentList = new List<UserRest>();

            char[] separators = new char[] { '\n' };
            string[] subs = Request.Form["studentlist"].ToString().Split(separators, StringSplitOptions.RemoveEmptyEntries);

            foreach (var sub in subs)
            {
                if (EmailValidator.IsValidEmail(sub.Trim()))
                {
                    var usr = new UserRest();
                    usr.UserEmail = sub.Trim();
                    usr.Claims = new Dictionary<string, string> { { Request.Form["claimname"].ToString(),
                                                                    Request.Form["claimvalue"].ToString() } };

                    studentList.Add(usr);
                }
                else
                {
                    string errmsg = string.Format("{0} is not a valid email address.", sub);
                    _logger.LogTrace("Input list of students is not valid. Entry {sub} is not a valid email address.", sub);
                    ModelState.AddModelError(string.Empty, errmsg);
                    return Page();
                }
            }

            try
            {
                _logger.LogTrace("List if students {StudentList}", studentList);
                await _authService.OnUpdateStudentListAsync(studentList);
                _logger.LogTrace("List of students was updated successfuly");
            }
            catch (Exception e)
            {
                ModelState.AddModelError(string.Empty, "List of students update failed.");
                _logger.LogError("List of students update failed. {e}", e);
                return Page();
            }
          
            return RedirectToPage();
        }

        public ActionResult OnGetUpdate()
        {
            _logger.LogTrace("Enter the update student list page");
            return Page();
        }
    }
}
