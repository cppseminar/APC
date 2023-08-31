using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using System;
using System.Net;
namespace presentation.Filters;

public class TestIPFilter : ResultFilterAttribute
{
    private readonly byte[] _allowedLowerBytes;
    private readonly byte[] _allowedUpperBytes;

    public TestIPFilter(string allowedIPLowerStr, string allowedIPUpperStr)
    {
        IPAddress allowedIPLower;
        IPAddress.TryParse(allowedIPLowerStr, out allowedIPLower);
        _allowedLowerBytes = allowedIPLower.GetAddressBytes();

        IPAddress allowedIPUpper;
        IPAddress.TryParse(allowedIPUpperStr, out allowedIPUpper);
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

    public override void OnResultExecuting(ResultExecutingContext context)
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
}


