using MongoDB.Bson.Serialization.Attributes;
using MongoDB.Bson;
using System.ComponentModel.DataAnnotations;

namespace testservice.Models
{
    // Response to count number of test runs request
    public class TestRunCount
    {
        [Required]
        public string TestCaseId { get; set; }

        [Required]
        public string UserEmail { get; set; }

        [Required]
        public int Count { get; set; }
    }
}
