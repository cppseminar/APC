using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using System;
using System.Collections.Generic;
using System.Net;
using presentation.Services;
namespace presentation.Filters;

public class PageIPFilter : GenericIPFilter, IResourceFilter
{
    public PageIPFilter(string IPLower, string IPUpper) : base(IPLower, IPUpper)
    {
    }

    public void OnResourceExecuting(ResourceExecutingContext context)
    {
        IPAddress clientIPAddress;
        IPAddress.TryParse(context.HttpContext.Connection.RemoteIpAddress?.ToString(), out clientIPAddress);
        if (!AddressWithinRange(clientIPAddress))
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


