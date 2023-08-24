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
        
        //[Authorize(Policy="Student")]
        public async Task LogConnection()
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

         [Authorize(Policy="Administrator")]
        public async Task GetConnectedUsersRecentAsync(){
            var response = await _monitoringService.GetConnectedUsersRecentAsync();
            var str = await response.Content.ReadAsStringAsync();
            await Clients.Caller.SendAsync("ReceiveUsers", str);
        }
    }
}