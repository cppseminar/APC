using System;
using Microsoft.AspNetCore.SignalR;
using System.Threading.Tasks;

namespace presentation.Hubs
{
    public class MonitoringHub: Hub
    {
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
            System.Console.WriteLine("SendMessage: " + user + " " + message);
            await Clients.All.SendAsync("ReceiveMessage", user, message);
        }
    }
}