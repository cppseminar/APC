using System.ComponentModel.DataAnnotations;

namespace presentation.Model
{
    public class Submission
    {
        public string Id { get; set; }
        public string UserEmail { get; set; }
        public string Content { get; set; }
        public string Name { get; set; }
        public string TaskId { get; set; }
        public override string ToString()
        {
            return $"{this.Id} - {this.UserEmail}";
        }
    }
}
