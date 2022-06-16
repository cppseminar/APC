using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Cosmos.Table;
using Microsoft.Extensions.Logging;
using userservice.Models;
using userservice.Services;

namespace userservice.Controllers
{
    [Route("[controller]")]
    [ApiController]
    public class UserController : ControllerBase
    {
        private ILogger<UserController> _logger;
        private UserDbService _service;

        public UserController(ILogger<UserController> logger, UserDbService service)
        {
            _logger = logger;
            _service = service;
        }

        [HttpGet]
        public async Task<IEnumerable<string>> OnGetAsync()
        {
            return await _service.GetAllUsersAsync();
        }

        [HttpGet("{email}")]
        public async Task<ActionResult<UserModel>> GetUserClaims([FromRoute]string email)
        {
            return await _service.GetUserAync(email);
        }

        [HttpPost]
        public async Task<IActionResult> UpdateListOfStudents([FromBody] List<UserModel> listOfStudents)
        {
            try
            {
                await _service.UpdateListOfStudents(listOfStudents);

                return StatusCode(201);
            }
            catch (Exception ex)
            {
                _logger.LogError($"Problem in [UploadListOfUsers] action: {ex.Message}");
                return StatusCode(500, "Upload failed. Please see the log.");
            }
        }
    }
}
