using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Authorization.Infrastructure;
using presentation.Model;

namespace presentation.Services
{
    public class AdminAuthorizationService
        : AuthorizationHandler<OperationAuthorizationRequirement>
    {
        // Admin can do absolutelty anything
        protected override Task HandleRequirementAsync(
            AuthorizationHandlerContext context,
            OperationAuthorizationRequirement requirement)
        {
            Console.WriteLine("Evaluating");
            if (!context.User.Identity.IsAuthenticated)
            {
                return Task.CompletedTask;
            }
            if (context.User.HasClaim(claim => claim.Type == "isAdmin" && claim.Value == "true"))
            {
                context.Succeed(requirement);
            }
            return Task.CompletedTask;
        }
    }

    public class TaskAuthorizationService
    {
    }

    public class SubmissionAuthorizationService
    {
    }

    public static class ClaimsPrincipalExtension
    {
        public static string GetEmail(this ClaimsPrincipal principal)
        {
            Claim emailClaim = principal.FindFirst(claim => claim.Type == ClaimTypes.Email);
            if (emailClaim == null)
            {
                throw new InvalidOperationException("User doesn't have email set up");
            }
            return emailClaim.Value;
        }
    }
}
