using System.ComponentModel.DataAnnotations;

namespace submissions.Data
{
    public class CosmosSettings : ICosmosSettings
    {
        [Required]
        [MinLength(5)]
        public string DatabaseName { get; set; }

        [Required]
        [MinLength(5)]
        public string ConnectionString { get; set; }
    }

    public interface ICosmosSettings
    {
        [Required]
        string DatabaseName { get; set; }
        string ConnectionString { get; set; }

    }
}
