using System;
using System.ComponentModel.DataAnnotations;
using System.Text.Json;
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
        public string RequiredIp { get; set; }

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

        // Called during update
        // Json Serialize must be called this way, because empty values in forms are
        // by asp replaced with nulls. These are then ignored by backend service.
        // What we need is empty string, not null. Therefore here it is handled
        // "by hand". And only for requiredIP field, that has highest possibility
        // of being in need of deletion.
        // Making it better I leave as an excercise for future developers
        public string ToJsonPatch()
        {
            var thisCopy = this;
            if (thisCopy.RequiredIp == null)
            {
                thisCopy.RequiredIp = string.Empty;
            }
            return JsonSerializer.Serialize(thisCopy);
        }
    }
}
