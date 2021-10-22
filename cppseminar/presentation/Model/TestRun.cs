using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace presentation.Model
{
    public class TestRun
    {
        public string TaskId { get; set; }
        public string SubmissionId { get; set; }
        public string TestCaseId { get; set; }
        public string CreatedBy { get; set; }
        public string TaskName { get; set; }
        public string TestCaseName { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime? FinishedAt { get; set; }
        public string Status { get; set; }
        public string Id { get; set; }
        public string Message { get; set; }
        public string Name { get; set; }
        public string Students { get; set; }
        public string Teachers { get; set; }
    }
}
