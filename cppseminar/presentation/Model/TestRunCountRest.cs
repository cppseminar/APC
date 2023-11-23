using System.ComponentModel.DataAnnotations;

namespace presentation.Model
{
    // Represents data returned from test service
    public class TestRunCountRest
    {
        [Required]
        public string TestCaseId { get; set; }
        [Required]
        public string UserEmail { get; set; }
        [Required]
        public int Count { get; set; }
    }
}
