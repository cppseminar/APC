using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;


namespace presentation.Model
{
    public class ConnectionLog
    {
        public ConnectionLog(string email, string timestamp){
            UserEmail = email;
            Timestamp = timestamp;
        }
        public ConnectionLog(){
        }
        public string UserEmail { get; set; }
        public string Timestamp { get; set; }
    }
}
