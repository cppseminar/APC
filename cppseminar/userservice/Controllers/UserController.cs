using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using userservice.Models;
using userservice.Services;

namespace userservice.Controllers;

[Route("[controller]")]
[ApiController]
public class UserController : ControllerBase
{
    private readonly ILogger<UserController> _logger;
    private readonly UsersService _service;

    public UserController(ILogger<UserController> logger, UsersService service)
    {
        _logger = logger;
        _service = service;
    }

    [HttpGet]
    public async Task<IEnumerable<string>> OnGetAsync()
    {
        var users = await _service.GetAsync();
        return users.Select(x => x.UserEmail);
    }

    [HttpGet("{email}")]
    public async Task<ActionResult<User>> GetUserClaims([FromRoute]string email)
    {
        try
        {
            return await _service.GetAsync(email);
        }
        catch (InvalidOperationException e)
        {
            _logger.LogWarning("User {user} not found. {e}", email, e);

            return NotFound();
        }
        catch (Exception e)
        {
            _logger.LogError("Exception occuret while retrieving user {email}. {e}", email, e);

            return StatusCode(500);
        }
    }

    [HttpPost]
    public async Task<IActionResult> UpdateListOfUsers([FromBody] List<User> users)
    {
        try
        {
            foreach (var user in users)
            {
                User dbUser = new();
                try
                {
                    dbUser = await _service.GetAsync(user.UserEmail);
                }
                catch (InvalidOperationException)
                {
                    _logger.LogInformation("User {email} not in database we create it.", user.UserEmail);

                    dbUser.UserEmail = user.UserEmail;
                    dbUser.Claims = new Dictionary<string, string>();

                    await _service.CreateAsync(dbUser);
                }

                _logger.LogTrace("Updating claims in db entry.");
                foreach (var item in user.Claims)
                {
                    dbUser.Claims[item.Key] = item.Value;
                }

                _logger.LogTrace("Saving to DB.");
                await _service.UpdateAsync(dbUser);
            }

            return StatusCode(201);
        }
        catch (Exception e)
        {
            _logger.LogError("Problem with updating of users action: {e}", e);

            return StatusCode(500, "Update failed.");
        }
    }
}
