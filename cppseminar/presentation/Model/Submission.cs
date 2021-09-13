namespace presentation.Model
{
    public class Submission
    {
        public string Id { get; set; }
        public string UserEmail { get; set; }
        public string Content { get; set; }
        public string Name { get; set; }
        public string TaskId { get; set; }
        public string TaskName { get; set; }

        public static Submission GenerateSubmission(
            Submission submission, TaskModel task, string email) => new()
        {
            Id = null,
            UserEmail = email,
            Content = submission.Content,
            Name = null,
            TaskId = task.Id,
            TaskName = task.Name
        };
    }
}
