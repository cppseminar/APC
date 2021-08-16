using System;
using System.ComponentModel.DataAnnotations;


namespace submissions.Models
{
    public class Submission
    {
        [Key]
        public Guid Id { get; set; }
        [Required]
        public string TaskId { get; set; }
        [Required]
        public string UserEmail { get; set; }
        public System.DateTime SubmittedOn { get; set; }


    }

    public class SubmissionRest
    {
        [Required]
        public string TaskId { get; set; }
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
            return new Submission()
            {
                Id = this._GeneratedId,
                TaskId = this.TaskId,
                UserEmail = this.UserEmail,
                SubmittedOn = DateTime.UtcNow,
            };
        }
    }
}
