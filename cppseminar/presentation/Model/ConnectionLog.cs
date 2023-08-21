using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;


namespace presentation.Model
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
