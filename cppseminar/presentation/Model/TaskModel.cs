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
        public DateTime? Ends { get; set; }
        public string Claim { get; set; }
    }
}
