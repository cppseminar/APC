
using Serilog;
using Serilog.Events;
using Serilog.Formatting.Compact;

namespace mqreadservice
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            builder.Services.AddControllers();

            if (Environment.GetEnvironmentVariable("LOG_PRETTY") == "1")
            {
                builder.Host.UseSerilog((ctx, lc) => lc
                .MinimumLevel.Verbose()
                .MinimumLevel.Override("Microsoft", LogEventLevel.Debug)
                .Enrich.FromLogContext()
                .WriteTo.Console());
            }
            else
            {
                builder.Host.UseSerilog((ctx, lc) => lc
                .MinimumLevel.Verbose()
                .MinimumLevel.Override("Microsoft", LogEventLevel.Debug)
                .Enrich.FromLogContext()
                .WriteTo.Console(new RenderedCompactJsonFormatter()));
            }

            var app = builder.Build();

            app.MapControllers();

            app.Run();
        }
    }
}
