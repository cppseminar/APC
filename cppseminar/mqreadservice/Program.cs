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
            builder.Services.AddSwaggerGen();

            var app = builder.Build();

            app.MapControllers();

            if (app.Environment.IsDevelopment())
{
                app.UseSwagger();
                app.UseSwaggerUI();
            }

            app.Run();
        }
    }
}
