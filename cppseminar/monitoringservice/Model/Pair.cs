namespace monitoringservice.Model;

public class Pair
{
    public string? Key { get; set; }
    public string? Value { get; set; }

    public Pair(string? key, string? value)
    {
        Key = key;
        Value = value;
    }
}