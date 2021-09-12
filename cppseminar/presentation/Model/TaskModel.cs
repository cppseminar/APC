using System;
using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Mvc.ModelBinding;

namespace presentation.Model
{
    public class TaskModel
    {
        [BindNever]
        public string Id { get; set; }
        [Required]
        public string Name { get; set; }
        public string CreatedBy { get; set; }
        [Required]
        public string Description { get; set; }
        [Required]
        public DateTime? Ends { get; set; }
        public string ClaimName { get; set; }
        public string ClaimValue { get; set; }

        public bool IsEnded()
        {
            if (Ends == null)
            {
                return false;
            }
            if (Ends < DateTime.UtcNow)
            {
                return true;
            }
            return false;
        }
    }
}
