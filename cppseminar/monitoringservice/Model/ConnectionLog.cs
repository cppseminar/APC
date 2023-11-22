using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;


namespace monitoringservice.Model
{
    public class ConnectionLog
    {
        public ConnectionLog(string email, DateTime timestamp){
            UserEmail = email;
            Timestamp = timestamp;
        }
        public ConnectionLog(){
        }
        public string UserEmail { get; set; }
        public DateTime Timestamp { get; set; }
    }
}
