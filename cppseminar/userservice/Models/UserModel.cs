using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Azure.Cosmos.Table;

namespace userservice.Models
{
    public class UserRow : TableEntity
    {
        public string UserEmail { get { return PartitionKey; } }
        public string ClaimType { get { return RowKey; } }
        public string ClaimValue { get; set; }

        public static explicit operator UserModel(UserRow row)
        {
            return new UserModel()
            {
                UserEmail = row.UserEmail
            };
        }

    }

    public class UserModel
    {
        // TODO: Try setting email verification
        public string UserEmail { get; set; }
        public IDictionary<string, string> Claims { get; set; }
    }
}
