using System;
using System.ComponentModel.DataAnnotations;

namespace testservice.Models
{
    public class TestCase
    {
        public string Id { get; set; }
        public DateTime CreatedAt { get; set; }
        [Required]
        public string Name { get; set; }
        [Required]
        public string TaskId { get; set; }
        [Required]
        public string DockerImage { get; set; }
        [Required]
        public int MaxRuns { get; set; }
        [Required]
        public string ClaimName { get; set; }
        [Required]
        public string ClaimValue { get; set; }
        [Required]
        public string CreatedBy { get; set; }

    }
}
