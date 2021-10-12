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
    // Admin can do absolutelty anything
    public class AdminAuthorizationService
        : AuthorizationHandler<OperationAuthorizationRequirement>
    {
        protected override Task HandleRequirementAsync(
            AuthorizationHandlerContext context,
            OperationAuthorizationRequirement requirement)
        {
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

    // Check that Users has claims required by Task
    public class TaskAuthorizationService
        : AuthorizationHandler<OperationAuthorizationRequirement, TaskModel>

    {
        protected override Task HandleRequirementAsync(
            AuthorizationHandlerContext context,
            OperationAuthorizationRequirement requirement,
            TaskModel task)
        {
            if (task == null || task.ClaimName == null || task.ClaimValue == null)
            {
                return Task.CompletedTask;
            }
            var taskClaim = context.User.FindFirst(
                claim => claim.Type == task.ClaimName && claim.Value == task.ClaimValue);
            if (taskClaim != null)
            {
                context.Succeed(requirement);
            }
            return Task.CompletedTask;
        }
    }

    // Check that user has claims required by test case
    public class TestCaseAuthorizationService
    : AuthorizationHandler<OperationAuthorizationRequirement, TestCaseRest>

    {
        protected override Task HandleRequirementAsync(
            AuthorizationHandlerContext context,
            OperationAuthorizationRequirement requirement,
            TestCaseRest testCase)
        {
            if (testCase == null || testCase.ClaimName == null || testCase.ClaimValue == null)
            {
                return Task.CompletedTask;
            }
            var caseClaim = context.User.FindFirst(
                claim => claim.Type == testCase.ClaimName && claim.Value == testCase.ClaimValue);
            if (caseClaim != null)
            {
                context.Succeed(requirement);
            }
            return Task.CompletedTask;
        }
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
        public static bool IsAdmin(this ClaimsPrincipal principal)
        {
            Claim adminClaim = principal.FindFirst(
                claim => claim.Type == "isAdmin" && claim.Value == "true");
            if (adminClaim == null)
            {
                return false;
            }
            return true;
        }

    }
}
