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
    }
}
