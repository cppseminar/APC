using System;
using System.Globalization;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace presentation.Converters;
public class DateTimeDifferenceConverter : JsonConverter<string>
{
    // when deserializing takes the timestamp string value and calculates the time difference between timestamp and current time, returns the result in string format
    public override string Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        if (reader.TokenType == JsonTokenType.String)
        {
            string dateTimeStr = reader.GetString();
            try{
                DateTime timestamp = DateTime.Parse(dateTimeStr, CultureInfo.InvariantCulture);

                TimeSpan difference = DateTime.UtcNow - timestamp;
                double secondsDifference = difference.TotalSeconds;

                return secondsDifference.ToString();
            }
            catch (Exception e){
                throw new Exception($"Deserialization failed {e}");
            }
            
        }

        throw new JsonException($"Unexpected token type: {reader.TokenType}");
    }

    public override void Write(Utf8JsonWriter writer, string value, JsonSerializerOptions options)
    {
        writer.WriteStringValue(value);
    }
}


