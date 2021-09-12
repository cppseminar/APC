using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization.Infrastructure;

namespace presentation.Model
{
    public class AuthorizationConstants
    {
        public static OperationAuthorizationRequirement Submit =
            new OperationAuthorizationRequirement() { Name = "Submit" };

    }
}
