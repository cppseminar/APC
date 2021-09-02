using System;
using System.ComponentModel.DataAnnotations;
using Newtonsoft.Json;

namespace submissions.Models
{
    public class WorkTask
    {
        public WorkTask ToDbForm()
        {
            return new WorkTask()
            {
                Id = Guid.NewGuid().ToString(),
                Name = this.Name,
                Claim = this.Claim ?? "",
                Description = this.Description,
                Ends = this.Ends,
                CreatedBy = this.CreatedBy,
                CreatedOn = DateTime.UtcNow
            };
        }

        public string Id { get; set; }
        [Required]
        public string Name { get; set; }
        public string Claim { get; set; }
        [Required]
        public string Description { get; set; }
        [Required]
        public string CreatedBy { get; set; }
        public DateTime CreatedOn { get; set; }
        public DateTime Ends
        {
            get
            {
                DateTime result = ends
                                  ?? new DateTime(DateTime.Now.Year + 1, 1, 1);
                return result;
            }
            set => ends = value;
        }
        private DateTime? ends = null;
    }
}
