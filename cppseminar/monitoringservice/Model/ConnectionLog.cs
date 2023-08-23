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