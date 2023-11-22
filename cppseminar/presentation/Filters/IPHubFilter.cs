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
        var remoteIpAddressStr = context.Context.GetHttpContext()?.Connection.RemoteIpAddress.ToString();
        var forwardedForHeaderStr = context.Context.GetHttpContext()?.Request.Headers["X-Forwarded-For"].FirstOrDefault();
        IPAddress remoteIPAddress = GetRemoteIP(remoteIpAddressStr, forwardedForHeaderStr);

        if (remoteIPAddress == null || !AddressWithinRange(remoteIPAddress))
        {
            System.Console.WriteLine($"IP Address failed to parse or not allowed in OnConnected. {remoteIpAddressStr} {forwardedForHeaderStr}");
            context.Context.Abort();
        }
        return next(context);
    }

    public async ValueTask<object?> InvokeMethodAsync(HubInvocationContext invocationContext, Func<HubInvocationContext, ValueTask<object?>> next)
    {
        var remoteIpAddressStr = invocationContext.Context.GetHttpContext()?.Connection.RemoteIpAddress.ToString();
        var forwardedForHeaderStr = invocationContext.Context.GetHttpContext()?.Request.Headers["X-Forwarded-For"].FirstOrDefault();
        IPAddress remoteIPAddress = GetRemoteIP(remoteIpAddressStr, forwardedForHeaderStr);
        if (remoteIPAddress == null || !AddressWithinRange(remoteIPAddress))
        {
            System.Console.WriteLine($"IP Address failed to parse or not allowed in invoke method. {remoteIpAddressStr} {forwardedForHeaderStr}");
            invocationContext.Context.Abort();
            return null;
        }
        return await next(invocationContext);
    }
}