using System;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
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
        app.Use((context, next) =>
        {
            context.Request.EnableBuffering();
            return next();
        });

        var logger = app.Services.GetRequiredService<ILogger<Program>>();

        app.MapGet("/monitoring/get/recents", async (StorageService db, HttpContext context) => {
            try
            {
                return await db.getConnectionLogsJsonAsync();
            }
            catch (Exception e)
            {
                logger.LogError("Exception occured while retrieving all ConnectionLog records. " + e);
                context.Response.StatusCode = 500;
                return "";
            }
        });

        app.MapPost("/monitoring/post/log", async (ConnectionLog connectionLog, StorageService db, HttpContext context) => {
            if (connectionLog.UserEmail == null || connectionLog.Timestamp == null)
            {
                context.Request.Body.Position = 0;
                string body = await new StreamReader(context.Request.Body).ReadToEndAsync();
                logger.LogWarning($"ConnectionLog not found in the request: {body}");
                context.Response.StatusCode = 400;
                return "";
            }
            else
            {
                try
                {
                    await db.setConnectionlogAsync(connectionLog);
                    return "";
                }
                catch (Exception e)
                {
                    logger.LogError("Exception occured while logging user connection. " + e);
                    context.Response.StatusCode = 500;
                    return "";
                }
            }
        });

        app.Run();
    }
}

