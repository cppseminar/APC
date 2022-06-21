using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using System.Security.Claims;
using Microsoft.AspNetCore.Authentication.OAuth;
using Microsoft.Extensions.Configuration;
using presentation.Model;

namespace presentation.Services
{
    // There is currently no way, to plug logger here
    // so this service throws exceptions like a maniac

    // TODO: Use different method to obtain claims, and add logging here
    public class AuthenticationService
    {
        private HttpClient _client = new HttpClient();

        public AuthenticationService(IConfiguration config)
        {
            string userServiceHost = config["API_GATEWAY"];

            _client.BaseAddress = new Uri(userServiceHost);
            _client.DefaultRequestHeaders.Accept.Clear();
            _client.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
        }

        public async Task<IEnumerable<string>> GetAllUsers()
        {
            HttpResponseMessage response = await _client.GetAsync("/user/");
            if (!response.IsSuccessStatusCode)
            {
                throw new OperationFailedException($"Error on claims retrieval {response.StatusCode}");
            }
            return await response.Content.ReadAsAsync<IEnumerable<string>>();
        }

        public async Task<IDictionary<string, string>> GetUserClaimsAsync(string userEmail)
        {
            HttpResponseMessage response = await _client.GetAsync($"/user/{userEmail}");
            if (!response.IsSuccessStatusCode)
            {
                throw new OperationFailedException($"Error on claims retrieval {response.StatusCode}");
            }
            UserRest user = await response.Content.ReadAsAsync<UserRest>();
            if (user.UserEmail != userEmail)
            {
                throw new OperationFailedException("Retrieved wrong user");
            }
            return user.Claims;
        }

        public async static Task OnCreateTicketAsync(AuthenticationService serviceInstance, OAuthCreatingTicketContext context)
        {
            Claim emailClaim = context.Identity.FindFirst(claim => claim.Type == ClaimTypes.Email);
            if (emailClaim == null)
            {
                throw new OperationFailedException("Email claim is not present in login");
            }
            IDictionary<string, string> claims = await serviceInstance.GetUserClaimsAsync(emailClaim.Value);
            if (claims.Count == 0)
            {
                // Don't let unknown users sign in
                context.Fail(new OperationFailedException());
                return;
            }
            foreach (var claimKV in claims)
            {
                context.Identity.AddClaim(new Claim(claimKV.Key, claimKV.Value));
            }
        }
    }
}
