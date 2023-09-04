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
    //private readonly string[] _allowedIpAddresses;
    private readonly List<Tuple<byte[], byte[]>> allowedIPRanges = new List<Tuple<byte[], byte[]>>();   

    public IPHubFilter(string[] allowedIpAddresses)
    {

        var length = allowedIpAddresses.Length;
        if (length < 2 && length > 0){
            IPAddress allowedIPLower;
            IPAddress.TryParse(allowedIpAddresses[0], out allowedIPLower);
            allowedIPRanges.Add(new Tuple<byte[], byte[]>(allowedIPLower.GetAddressBytes(),new byte[]{}));
        }
        else{
            IPAddress allowedIPUpper;
            IPAddress allowedIPLower;
            for(var i = 0; i < length; i+=2){
                IPAddress.TryParse(allowedIpAddresses[i], out allowedIPLower);
                if((i+1) < length){
                    IPAddress.TryParse(allowedIpAddresses[i+1], out allowedIPUpper);
                    allowedIPRanges.Add(new Tuple<byte[], byte[]>(allowedIPLower.GetAddressBytes(), allowedIPUpper.GetAddressBytes()));
                }
                else{
                     allowedIPRanges.Add(new Tuple<byte[], byte[]>(allowedIPLower.GetAddressBytes(),new byte[]{}));
                }
            }
        }
        
    }

     public Task OnConnectedAsync(HubLifetimeContext context, Func<HubLifetimeContext, Task> next)
    {
        var remoteIpAddresStr = context.Context.GetHttpContext()?.Connection.RemoteIpAddress.ToString();
        IPAddress remoteIPAddress;
        IPAddress.TryParse(remoteIpAddresStr, out remoteIPAddress);
        
        if (!AddressWithinRange(remoteIPAddress))
        {
           System.Console.WriteLine("IP adress not allowed in onconnected "+remoteIpAddresStr);
           context.Context.Abort();
        }        
        return next(context);
    }
    private bool AddressWithinRange(IPAddress clientAddress){
        byte[] clientAddressBytes = clientAddress.GetAddressBytes();
        foreach(var range in allowedIPRanges){
            for(int i=0; i < range.Item1.Length; i++){
                if(clientAddressBytes[i]< range.Item1[i] || (range.Item2.Length != 0 && clientAddressBytes[i]> range.Item2[i])){
                    return false;
                }
            }
        }
        return true;
    }

    public async ValueTask<object?> InvokeMethodAsync(HubInvocationContext invocationContext, Func<HubInvocationContext, ValueTask<object?>> next)
    {
        var remoteIpAddresStr = invocationContext.Context.GetHttpContext()?.Connection.RemoteIpAddress.ToString();
        IPAddress remoteIPAddress;
        IPAddress.TryParse(remoteIpAddresStr, out remoteIPAddress);

        if (!AddressWithinRange(remoteIPAddress))
        {
            System.Console.WriteLine("IP adress not allowed in invoke method "+ remoteIpAddresStr);
            invocationContext.Context.Abort();
            return null;
        }

        return await next(invocationContext);
    }
}
