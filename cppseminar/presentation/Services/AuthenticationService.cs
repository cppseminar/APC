using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authentication.OAuth;
using presentation.Model;

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
