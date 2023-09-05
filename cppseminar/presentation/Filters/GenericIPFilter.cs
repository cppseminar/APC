using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using System;
using System.Collections.Generic;
using System.Net;
using presentation.Services;
namespace presentation.Filters;

public class GenericIPFilter
{
    private readonly byte[] _allowedLowerBytes;
    private readonly byte[] _allowedUpperBytes;

    public GenericIPFilter(string allowedIPLowerStr, string allowedIPUpperStr)
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

    public bool AddressWithinRange(IPAddress clientAddress)
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
    public IPAddress GetRemoteIP(string remoteIpAddresStr, string forwardedForHeader){
        IPAddress remoteIPAddress;
        // if X-Forwarded-For is not empty
        if(!string.IsNullOrEmpty(forwardedForHeader)){
            System.Console.WriteLine("Forwarded-For " + forwardedForHeader);
            // check if the header is a valid IP address
            if(IPAddress.TryParse(forwardedForHeader, out remoteIPAddress)){
                return remoteIPAddress;
                }
        }
        // if X-Forwarded-For is empty or not a valid IP address continue with remoteIPAddressStr
        if (IPAddress.TryParse(remoteIpAddresStr, out remoteIPAddress))
        {
            return remoteIPAddress;
        }
        return null;
    }    
}