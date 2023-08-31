using Microsoft.AspNetCore.SignalR;
using System;
using System.Linq;
using System.Threading.Tasks;
namespace presentation.Filters;
public class IPHubFilter : IHubFilter
{
    private readonly string[] _allowedIpAddresses;

    public IPHubFilter(string[] allowedIpAddresses)
    {
        _allowedIpAddresses = allowedIpAddresses ?? throw new ArgumentNullException(nameof(allowedIpAddresses));
    }

     public Task OnConnectedAsync(HubLifetimeContext context, Func<HubLifetimeContext, Task> next)
    {
        var remoteIpAddress = context.Context.GetHttpContext()?.Connection.RemoteIpAddress;
        System.Console.WriteLine(remoteIpAddress);

        if (remoteIpAddress != null && !_allowedIpAddresses.Contains(remoteIpAddress.ToString()))
        {
            System.Console.WriteLine("IP adress not allowed in onconnected");
           context.Context.Abort();
        }        
        return next(context);
    }

    public async ValueTask<object?> InvokeMethodAsync(HubInvocationContext invocationContext, Func<HubInvocationContext, ValueTask<object?>> next)
    {
        var remoteIpAddress = invocationContext.Context.GetHttpContext()?.Connection.RemoteIpAddress;
        System.Console.WriteLine(remoteIpAddress);

        if (remoteIpAddress != null && !_allowedIpAddresses.Contains(remoteIpAddress.ToString()))
        {
            System.Console.WriteLine("IP adress not allowed");
            invocationContext.Context.Abort();
            return null;
        }

        return await next(invocationContext);
    }
}
