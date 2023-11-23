using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.ModelBinding;

namespace presentation.Model
{
    public class TestCaseRest
    {
        [BindNever]
        public string Id { get; set; }
        [BindNever]
        public string CreatedBy { get; set; }
        [BindNever]
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        [Required]
        public string Name { get; set; }
        [Required]
        public string TaskId { get; set; }
        [Required]
        public string DockerImage { get; set; }
        [Required]
        [Range(0, 100)]
        public int MaxRuns { get; set; }
        [Required]
        public string ClaimName { get; set; }
        [Required]
        public string ClaimValue { get; set; }

        // This is only helper field, that is not returned from REST, it is used only internally
        // It is number of tests, that were already submitted for this test case, by logged in user
        public int? SubmittedCount { get; set; } = null;
    }
}
