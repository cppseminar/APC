using System;
using System.Text.Json.Serialization;


namespace presentation.Model;

public class ConnectionLog
{
    public string UserEmail { get; set; }
    public DateTime Timestamp { get; set; }

    public ConnectionLog(string email, DateTime timestamp)
    {
        UserEmail = email;
        Timestamp = timestamp;
    }

}