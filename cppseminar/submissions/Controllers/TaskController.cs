using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using submissions.Data;
using submissions.Models;

// For more information on enabling Web API for empty projects, visit https://go.microsoft.com/fwlink/?LinkID=397860

namespace submissions.Controllers
{
    [Route("tasks/v1")]
    [ApiController]
    public class TaskController : ControllerBase
    {
        public TaskController(CosmosContext context)
        {
            _context = context;
        }
        // GET: api/<TaskController>
        [HttpGet]
        public IAsyncEnumerable<WorkTask> Get()
        {
            return _context.Tasks.AsAsyncEnumerable();
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<WorkTask>> Get(string id)
        {
            var result = await _context.Tasks.FirstOrDefaultAsync(task => task.Id == id);
            if (result == null)
            {
                return NotFound();
            }
            return result;
        }

        // POST api/<TaskController>
        [HttpPost]
        public async Task<ActionResult> PostAsync([FromBody] WorkTask task)
        {
            WorkTask fullTask = task.ToDbForm();
            _context.Tasks.Add(fullTask);
            await _context.SaveChangesAsync();
            return CreatedAtAction("Get", fullTask);
            
        }

        private CosmosContext _context = null;
    }
}
