using System.ComponentModel.DataAnnotations;

namespace presentation.Model
{
    public class UserListChange
    {
        [Required]
        public string UserList { get; set; }
        [Required]
        public string ClaimName { get; set; }
        [Required]
        public string ClaimValue { get; set; }

    }
}
