using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.AspNetCore.Mvc;
using System.Net;
namespace presentation.Filters;
public class TestIPFilter : ResultFilterAttribute
{
    private readonly IPAddress _allowedIPAddress;

    public TestIPFilter(string allowedIPAddress)
    {
        IPAddress.TryParse(allowedIPAddress, out _allowedIPAddress);
    }

    public override void OnResultExecuting(ResultExecutingContext context)
    {
        System.Console.WriteLine("On result executing is here");
        string remoteIpAddress = context.HttpContext.Connection.RemoteIpAddress?.ToString();

        if (remoteIpAddress != _allowedIPAddress?.ToString())
        {
            context.Result = new ContentResult
            {
                StatusCode = (int)HttpStatusCode.Forbidden,
                Content = "Access denied."
            };
        }
    }
}


