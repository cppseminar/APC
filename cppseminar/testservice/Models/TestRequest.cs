using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace testservice.Models
{
    public class TestRequest
    {
        [Required]
        public string TaskId { get; set; }
        [Required]
        public string SubmissionId { get; set; }
        [Required]
        public string TestCaseId { get; set; }
        [Required]
        public string CreatedBy { get; set; }
        [Required]
        public string TaskName { get; set; }
        [Required]
        public string TestCaseName { get; set; }
        [Required]
        public string ContentUrl { get; set; }
    }
}
