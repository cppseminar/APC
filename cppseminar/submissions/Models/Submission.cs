using System;
using System.ComponentModel.DataAnnotations;


namespace submissions.Models
{
    public class Submission
    {
        public string Id { get; set; }
        [Required]
        public string TaskId { get; set; }
        [Required]
        public string UserEmail { get; set; }
        // Name is combination of task name and submission date
        public string Name { get; set; }
        public string TaskName { get; set; }
        public System.DateTime SubmittedOn { get; set; }
    }

    public class SubmissionRest
    {
        [Required]
        public string TaskId { get; set; }
        [Required]
        public string TaskName { get; set; }
        [Required]
        public string UserEmail { get; set; }
        [Required]
        public string Content { get; set; }
        // Readonly properties:
        public System.DateTime SubmittedOn { get; }
        public string Id { get; }

        // Shared for submission in db and file storage
        private Guid _GeneratedId = Guid.NewGuid();

        public Submission GenerateSubmission()
        {
            var timeNow = DateTime.UtcNow;
            return new Submission()
            {
                Id = this._GeneratedId.ToString(),
                TaskId = this.TaskId,
                UserEmail = this.UserEmail,
                SubmittedOn = timeNow,
                Name = $"{TaskName} on {timeNow}",
                TaskName = this.TaskName
            };
        }
    }
}
