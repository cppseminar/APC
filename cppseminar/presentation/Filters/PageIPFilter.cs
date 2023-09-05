using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using System;
using System.Collections.Generic;
using System.Net;
using presentation.Services;
using System.Linq;
namespace presentation.Filters;

public class PageIPFilter : GenericIPFilter, IResourceFilter
{
    public PageIPFilter(string IPLower, string IPUpper) : base(IPLower, IPUpper)
    {
    }

    public void OnResourceExecuting(ResourceExecutingContext context)
    {
        
        var remoteIpAddresStr = context.HttpContext.Connection.RemoteIpAddress.ToString();
        var forwardedForHeader = context.HttpContext.Request.Headers["X-Forwarded-For"].FirstOrDefault();
        IPAddress clientIPAddress = GetRemoteIP(remoteIpAddresStr, forwardedForHeader);

        if (clientIPAddress == null || !AddressWithinRange(clientIPAddress))
        {
            context.Result = new ContentResult
            {
                StatusCode = (int)HttpStatusCode.Forbidden,
                Content = "Access denied."
            };
        }
    }

    public void OnResourceExecuted(ResourceExecutedContext context)
    {
    }
}


