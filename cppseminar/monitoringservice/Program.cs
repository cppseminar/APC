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

        app.MapGet("/monitoring/redis/get/all", async (StorageService db) => {
            System.Console.WriteLine("GET /redis/get/all");
            return await db.getEveryKeyValueJsonAsync();
        });

        app.MapGet("/monitoring/redis/get/key/{key}", async (string key, StorageService db, HttpContext context) => {
            System.Console.WriteLine($"GET /redis/get/key/, key={key}");
            
            string value = await db.getValueAsync(key);
            if (value == null)
            {
                context.Response.StatusCode = 404;
                return "";
            }
            else
            {
                return value;
            }
        });

        app.MapPost("/monitoring/redis/post/pair", async (Pair pair, StorageService db, HttpContext context) => {
            System.Console.WriteLine($"POST /redis/post/pair: {pair.Key} {pair.Value}");
            if (!isValidPair(pair))
            {
                context.Response.StatusCode = 400;
                return "";
            }
            else
            {
                await db.setPairAsync(pair);
                return "OK\n";
            }
        });

        app.MapPost("/monitoring/redis/post/list/append", async (Pair pair, StorageService db, HttpContext context) => {
            System.Console.WriteLine($"POST /redis/post/list/append: {pair.Key} {pair.Value}");
            if (!isValidPair(pair))
            {
                context.Response.StatusCode = 400;
                return "";
            }
            else
            {
                await db.appendListPairAsync(pair);
                return "OK\n";
            }
        });

        app.MapGet("/monitoring/redis/get/list/all", async (StorageService db) => {
            System.Console.WriteLine("GET /redis/get/list/all");
            return await db.getEveryListJsonAsync();
        });

        app.MapGet("/monitoring/get/recents", async (StorageService db) => {
            return "This is a test.";
        });

        app.Run();
    }

    private static bool isValidPair(Pair pair)
    {
        return !(pair.Key == null || pair.Value == null);
    }
}

