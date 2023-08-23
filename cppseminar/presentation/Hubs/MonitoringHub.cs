using System;
using Microsoft.AspNetCore.SignalR;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http.Features;
using presentation.Services;
using presentation.Model;
using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using System.Text.Json;


namespace presentation.Hubs
{
    public class MonitoringHub: Hub
    {
        private MonitoringService _monitoringService;
        public MonitoringHub(MonitoringService monitoringService){
            _monitoringService = monitoringService;
        }
<<<<<<< HEAD
        // public override Task OnConnectedAsync()
        // {  
        //     System.Console.WriteLine("Client connected " + Context.ConnectionId);
        //     return base.OnConnectedAsync();  
        // }  

        // public override async Task OnDisconnectedAsync(Exception? exception)
        // {
        //     System.Console.WriteLine("Client disconnected " + Context.ConnectionId);
        //     await base.OnDisconnectedAsync(exception);
        // }
        
<<<<<<< HEAD
=======
        [Authorize(Policy="Student")]
>>>>>>> 23b70a5 (Added dynamic table refreshing in monitoring page)
        public async Task SendMessage(string user, string message)
=======
        
        //[Authorize(Policy="Student")]
        public async Task LogConnection()
>>>>>>> 0fcbfd2 (SignalR hub pulls user email from claims + 1st version of connection logging in redis)
        {
            string userEmail = "";
            foreach (Claim claim in Context.User.Claims) {
                if (claim.Type == "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress")
                {
                    userEmail = claim.Value;
                    break;
                }
            }
            var connectionLog = new ConnectionLog(userEmail, DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"));
            _monitoringService.LogConnectionAsync(connectionLog);
        }
        public async Task GetConnectedUsersRecentAsync(){
            var response = _monitoringService.GetConnectedUsersRecentAsync();
            System.Console.WriteLine(response);
            var test = JsonSerializer.Serialize(response);
            System.Console.WriteLine(test);
            await Clients.Caller.SendAsync("ReceiveUsers", response, "OK");
        }
    }
}