using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using presentation.Model;
using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace presentation.Services
{
    public class UserService
    {
        private HttpClient _client = new HttpClient();

        public UserService(IConfiguration config)
        {
            string userServiceHost = config["API_GATEWAY"];

            _client.BaseAddress = new Uri(userServiceHost);
            _client.DefaultRequestHeaders.Accept.Clear();
            _client.DefaultRequestHeaders.Accept.Add(
                new MediaTypeWithQualityHeaderValue("application/json"));
        }

        public async Task OnUpdateUserListAsync(List<UserRest> userList)
        {
            string userListAsJson = JsonSerializer.Serialize(userList);

            var stringContent = new StringContent(userListAsJson, Encoding.UTF8, "application/json");

            HttpResponseMessage response = await _client.PostAsync("/user/", stringContent);

            if (!response.IsSuccessStatusCode)
            {
                throw new OperationFailedException($"Error with updating list of users {response.StatusCode}");
            }
        }
    }
}
