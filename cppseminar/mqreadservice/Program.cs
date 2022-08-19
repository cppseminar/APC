using Microsoft.AspNetCore.Builder;

namespace mqreadservice
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            builder.Services.AddControllers();

            builder.Services.AddEndpointsApiExplorer();

            var app = builder.Build();

            app.MapControllers();

            app.Run();
        }
    }
}
