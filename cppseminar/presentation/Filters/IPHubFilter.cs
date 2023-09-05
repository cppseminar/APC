using Microsoft.AspNetCore.SignalR;
using System;
using System.Linq;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
namespace presentation.Filters;

public class IPHubFilter : GenericIPFilter, IHubFilter
{
    public IPHubFilter(string IPLower, string IPUpper) : base(IPLower, IPUpper)
    {
    }

    public Task OnConnectedAsync(HubLifetimeContext context, Func<HubLifetimeContext, Task> next)
    {
        var remoteIpAddresStr = context.Context.GetHttpContext()?.Connection.RemoteIpAddress.ToString();
        var forwardedForHeader = context.Context.GetHttpContext()?.Request.Headers["X-Forwarded-For"].FirstOrDefault();
        IPAddress remoteIPAddress = GetRemoteIP(remoteIpAddresStr, forwardedForHeader);
        if (remoteIPAddress == null || !AddressWithinRange(remoteIPAddress))
        {
            System.Console.WriteLine("IP Address failed to parse or not allowed in OnConnected. " + remoteIpAddresStr);
            context.Context.Abort();
        }
        return next(context);
    }

    public async ValueTask<object?> InvokeMethodAsync(HubInvocationContext invocationContext, Func<HubInvocationContext, ValueTask<object?>> next)
    {
        var remoteIpAddresStr = invocationContext.Context.GetHttpContext()?.Connection.RemoteIpAddress.ToString();
        var forwardedForHeader = invocationContext.Context.GetHttpContext()?.Request.Headers["X-Forwarded-For"].FirstOrDefault();
        IPAddress remoteIPAddress = GetRemoteIP(remoteIpAddresStr, forwardedForHeader);
        if (remoteIPAddress == null || !AddressWithinRange(remoteIPAddress))
        {
            System.Console.WriteLine("IP Address failed to parse or not allowed in invoke method. " + remoteIpAddresStr);
            invocationContext.Context.Abort();
            return null;
        }
        return await next(invocationContext);
    }
}