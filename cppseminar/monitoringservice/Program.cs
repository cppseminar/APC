using System;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using monitoringservice.Services;
using monitoringservice.Model;

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

        app.MapGet("/redis/get/all", async (StorageService db) => {
            System.Console.WriteLine("GET /redis/get/all");
            return await db.getEveryKeyValueJsonAsync();
        });

        app.MapGet("/redis/get/key/{key}", async (string key, StorageService db) => {
            System.Console.WriteLine($"GET /redis/get/key/, key={key}");
            string value = await db.getValueAsync(key);
            if (value == null)
                return "404\n"; // TODO - 404 status
            else
                return value;
        });

        app.MapPost("/redis/post", async (Pair pair, StorageService db) => {
            System.Console.WriteLine($"POST /redis/post: {pair.Key} {pair.Value}");
            if (pair.Key == null || pair.Value == null)
                return "Bad request\n"; // TODO - 400 status

            await db.setPairAsync(pair.Key, pair.Value);
            return "OK\n";
        });

        app.Run();
    }
}

