using System;
using Microsoft.AspNetCore.SignalR;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http.Features;
using presentation.Services;
using presentation.Model;


namespace presentation.Hubs
{
    public class MonitoringHub: Hub
    {
        private MonitoringService _monitoringService;
        public MonitoringHub(MonitoringService monitoringService){
            _monitoringService = monitoringService;
        }
        public override Task OnConnectedAsync()
        {  
            System.Console.WriteLine("Client connected " + Context.ConnectionId);
            return base.OnConnectedAsync();  
        }  

        public override async Task OnDisconnectedAsync(Exception? exception)
        {
            System.Console.WriteLine("Client disconnected " + Context.ConnectionId);
            await base.OnDisconnectedAsync(exception);
        }
        
        public async Task SendMessage(string user, string message)
        {
            System.Console.WriteLine();
            System.Console.WriteLine("SendMessage: " + user + " " + message);
            await Clients.All.SendAsync("ReceiveMessage", user, message);
        }
        public async Task GetConnectedUsers(string email){
            var response = _monitoringService.Test();
            await Clients.Caller.SendAsync("ReceiveUsers", response, "OK");
        }
    }
}