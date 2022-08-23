using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

using submissions.Models;
using submissions.Services;

namespace submissions.Controllers
{
    [Route("tasks")]
    [ApiController]
    public class TaskController : ControllerBase
    {
        public TaskController(TasksService tasks, ILogger<SubmissionController> logger)
        {
            _tasks = tasks;
            _logger = logger;
        }

        [HttpGet]
        public async Task<ActionResult<List<WorkTask>>> Get()
        {
            try
            {
                return await _tasks.GetAsync(30);
            }
            catch (Exception e)
            {
                _logger.LogError("Error during retrieval of data. {e}", e);
                return StatusCode(500);
            }
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<WorkTask>> Get(string id)
        {
            try
            {
                return await _tasks.GetAsync(id);
            }
            catch (Exception e)
            {
                _logger.LogWarning("Cannot find task with id {id}. {e}", id, e);
                return NotFound();
            }
        }

        [HttpPost]
        public async Task<ActionResult> PostAsync([FromBody] WorkTask task)
        {
            try
            {
                await _tasks.CreateAsync(task);

                return CreatedAtAction("Get", task);
            }
            catch (Exception e)
            {
                _logger.LogError("Error during creating of task {task}. {e}", JsonSerializer.Serialize(task), e);
                return StatusCode(500);
            }
        }

        private readonly TasksService _tasks = null;
        private readonly ILogger<SubmissionController> _logger = null;
    }
}
