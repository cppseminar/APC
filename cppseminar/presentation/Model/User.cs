using System;
using System.Collections.Generic;

namespace presentation.Model
{
    public sealed class UserRest
    {
        public string UserEmail { get; set; }
        public IDictionary<string, string> Claims { get; set; }
    }
}
