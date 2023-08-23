using System;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using monitoringservice.Model;
using monitoringservice.Services;

namespace monitoringservice;

public class Program
{
    public static void Main(string[] args)
    {
        var builder = WebApplication.CreateBuilder(args);
        builder.Services.AddSingleton<StorageService>();
        var app = builder.Build();

        if (!app.Environment.IsDevelopment())
        {
            app.UseExceptionHandler("/Error");
        }

        app.MapGet("/monitoring/get/recents", async (StorageService db) => {
            System.Console.WriteLine("GET /monitoring/get/recents");
            return await db.getConnectionLogsJsonAsync();
        });

        app.MapPost("/monitoring/post/log", async (ConnectionLog connectionLog, StorageService db, HttpContext context) => {
            System.Console.WriteLine($"POST monitoring/post/log: {connectionLog.UserEmail} {connectionLog.Timestamp}");
            if (connectionLog.UserEmail == null || connectionLog.Timestamp == null)
            {                
                context.Response.StatusCode = 400;
                return "";
            }
            else
            {
                await db.setConnectionlogAsync(connectionLog);
                return "";
            }
        });

        app.Run();
    }
}

