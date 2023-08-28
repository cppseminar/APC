using System;

namespace presentation.Model;

public class ConnectionLogTimeDiff
{
    public string UserEmail { get; set; }
    public double Seconds { get; set; }

    public ConnectionLogTimeDiff(ConnectionLog connectionLog)
    {
        UserEmail = connectionLog.UserEmail;
        Seconds = (double)(DateTime.UtcNow - connectionLog.Timestamp).TotalSeconds;
    }
}