using System;
using Microsoft.AspNetCore.SignalR;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http.Features;
using presentation.Services;
using presentation.Model;
using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using System.Text.Json;
using System.Collections.Generic;


namespace presentation.Hubs
{
    public class MonitoringHub: Hub
    {
        private MonitoringService _monitoringService;
        public MonitoringHub(MonitoringService monitoringService){
            _monitoringService = monitoringService;
        }

        [Authorize]
        public async Task LogConnection()
        {
            string userEmail = Context.User.FindFirst(claim => claim.Type == ClaimTypes.Email).Value;
            var connectionLog = new ConnectionLog(userEmail, DateTime.UtcNow);
            await _monitoringService.LogConnectionAsync(connectionLog);
        }

        [Authorize(Policy="Administrator")]
        public async Task GetConnectedUsersRecentAsync()
        {
            var responseData = await _monitoringService.GetConnectedUsersRecentAsync();
            if (responseData == null)
            {
                 await Clients.Caller.SendAsync("ErrorGettingUsers", "Monitoring service responded with null");
            }
            else
            {
                var connectionLogTimeDiffList = new List<ConnectionLogTimeDiff>();
                foreach (var connectionLog in responseData)
                {
                    connectionLogTimeDiffList.Add(new ConnectionLogTimeDiff(connectionLog));
                }
                connectionLogTimeDiffList.Sort((log1, log2) => string.Compare(log1.UserEmail, log2.UserEmail));
                await Clients.Caller.SendAsync("ReceiveUsers", JsonSerializer.Serialize(connectionLogTimeDiffList));
            }
        }
    }
}