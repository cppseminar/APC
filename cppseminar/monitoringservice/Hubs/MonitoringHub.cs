using Microsoft.AspNetCore.SignalR;

namespace MonitoringService.Hubs
{
    public class MonitoringHub : Hub
    {
        public async Task SendMessage(string user, string message)
        {
            await Clients.All.SendAsync("ReceiveMessage", user, message);
        }
    }
}