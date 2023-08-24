<<<<<<< HEAD
namespace monitoringservice.Model;

public class ConnectionLog
{
    public string? UserEmail { get; set; }
    public string? Timestamp { get; set; }

    public ConnectionLog(string? email, string? timestamp)
    {
        UserEmail = email;
        Timestamp = timestamp;
    }
}
=======
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
>>>>>>> a09bc53 (Fixed errors with ConnectionLog in monitoringService)
