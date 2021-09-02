using System.Threading.Tasks;
using Microsoft.AspNetCore.Authentication.OAuth;

namespace presentation.Services
{
    public class AuthenticationService
    {

        public async static Task OnCreateTicketAsync(OAuthCreatingTicketContext context)
        {
            await Task.Delay(0);
        }
    }
}
