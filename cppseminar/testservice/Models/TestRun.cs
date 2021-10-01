using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace testservice.Models
{
    public class TestRun
    {
        public TestRun()
        {

        }
        public TestRun(TestRequest request)
        {
            TaskId = request.TaskId;
            SubmissionId = request.SubmissionId;
            TestCaseId = request.TestCaseId;
            CreatedBy = request.CreatedBy;
            TaskName = request.TaskName;
            TestCaseName = request.TestCaseName;
            CreatedAt = DateTime.UtcNow;
            FinishedAt = null;
            Id = Guid.NewGuid().ToString();
            Name = $"Test run for {SubmissionId}";
            Status = "Requested";
            Message = "Test will start shortly."
            + " If you don't see results in few hours, please contact your teacher";
        }
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
    }
}