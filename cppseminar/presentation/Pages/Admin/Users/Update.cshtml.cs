using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.Extensions.Logging;
using presentation.Helpers;
using presentation.Model;
using presentation.Services;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace presentation.Pages.Admin.Users;

public class UpdateModel : PageModel
{
    public UpdateModel(ILogger<UpdateModel> logger, UserService userService)
    {
        _logger = logger;
        _userService = userService;
    }

    public void OnGet()
    {
    }

    public async Task<ActionResult> OnPostAsync()
    {
        _logger.LogTrace("CreateModel {CreateModel} submitted", NewUserList);

        if (!ModelState.IsValid)
        {
            _logger.LogTrace("Submitted TaskModel is invalid {errors}", ModelState.Values);
            return Page();
        }
        else
        {

            List<UserRest> userList = new();

            char[] separators = new char[] { '\n' };
            string[] subs = NewUserList.UserList.Split(separators, StringSplitOptions.RemoveEmptyEntries);

            foreach (var sub in subs)
            {
                if (EmailValidator.IsValidEmail(sub.Trim()))
                {
                    var usr = new UserRest
                    {
                        UserEmail = sub.Trim(),
                        Claims = new Dictionary<string, string> { { NewUserList.ClaimName,
                                                                    NewUserList.ClaimValue } }
                    };

                    userList.Add(usr);
                }
                else
                {
                    string errmsg = string.Format("{0} is not a valid email address.", sub);
                    _logger.LogTrace("Input list of users is not valid. Entry {sub} is not a valid email address.", sub);
                    ModelState.AddModelError(String.Empty, errmsg);

                    return Page();
                }
            }

            try
            {
                _logger.LogTrace("List if users {userList}", userList);
                await _userService.OnUpdateUserListAsync(userList);
                _logger.LogTrace("List of users was updated successfuly");

                return RedirectToPage("/Admin/Users/Index");
            }
            catch (Exception e)
            {
                ModelState.AddModelError(string.Empty, "List of users update failed.");
                _logger.LogError("List of users update failed. {e}", e);
                return Page();
            }


        }
    }

    [BindProperty]
    public UserListChange NewUserList { get; set; }

    private readonly UserService _userService = null;
    private readonly ILogger<UpdateModel> _logger = null;
}
