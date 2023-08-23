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
        {
            System.Console.WriteLine();
            System.Console.WriteLine("SendMessage: " + user + " " + message);
            System.Console.WriteLine(Context.User.Claims);
            foreach (Claim claim in Context.User.Claims){
                System.Console.WriteLine(claim.Type);
                System.Console.WriteLine(claim.Value);
            }
            await Clients.All.SendAsync("ReceiveMessage", user, message);
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