using Microsoft.AspNetCore.SignalR;
using System;
using System.Linq;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
namespace presentation.Filters;

public class IPHubFilter : IHubFilter
{
    private readonly byte[] _allowedLowerBytes;
    private readonly byte[] _allowedUpperBytes;

    public IPHubFilter(string allowedIPLowerStr, string allowedIPUpperStr)
    {
        IPAddress allowedIPLower;
        IPAddress allowedIPUpper;
        if (!IPAddress.TryParse(allowedIPLowerStr, out allowedIPLower) || !IPAddress.TryParse(allowedIPUpperStr, out allowedIPUpper))
        {
            throw new ArgumentException($"Failed to parse IP address: {allowedIPLowerStr} {allowedIPUpperStr}");
        }
        
        _allowedLowerBytes = allowedIPLower.GetAddressBytes();
        _allowedUpperBytes = allowedIPUpper.GetAddressBytes();

        // Check if lower bound is indeed lower
        for (int i = 0; i < _allowedLowerBytes.Length; i++)
        {
            if (_allowedLowerBytes[i] > _allowedUpperBytes[i])
            {
                throw new ArgumentException("Invalid range of IP addresses.");
            }
        }
    }

    private bool AddressWithinRange(IPAddress clientAddress)
    {
        byte[] clientAddressBytes = clientAddress.GetAddressBytes();
        for (int i = 0; i < _allowedLowerBytes.Length; i++)
        {
            if (clientAddressBytes[i] < _allowedLowerBytes[i] || clientAddressBytes[i] > _allowedUpperBytes[i])
            {
                return false;
            }
        }
        return true;
    }

    public Task OnConnectedAsync(HubLifetimeContext context, Func<HubLifetimeContext, Task> next)
    {
        var remoteIpAddresStr = context.Context.GetHttpContext()?.Connection.RemoteIpAddress.ToString();
        IPAddress remoteIPAddress;
        if (!IPAddress.TryParse(remoteIpAddresStr, out remoteIPAddress) || !AddressWithinRange(remoteIPAddress))
        {
            System.Console.WriteLine("IP Address failed to parse or not allowed in OnConnected. " + remoteIpAddresStr);
            context.Context.Abort();
        }
        return next(context);
    }

    public async ValueTask<object?> InvokeMethodAsync(HubInvocationContext invocationContext, Func<HubInvocationContext, ValueTask<object?>> next)
    {
        var remoteIpAddresStr = invocationContext.Context.GetHttpContext()?.Connection.RemoteIpAddress.ToString();
        IPAddress remoteIPAddress;

        if (!IPAddress.TryParse(remoteIpAddresStr, out remoteIPAddress) || !AddressWithinRange(remoteIPAddress))
        {
            System.Console.WriteLine("IP Address failed to parse or not allowed in invoke method. " + remoteIpAddresStr);
            invocationContext.Context.Abort();
            return null;
        }
        return await next(invocationContext);
    }
}