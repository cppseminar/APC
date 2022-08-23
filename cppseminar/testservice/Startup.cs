using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using testservice.Models;
using testservice.Services;

namespace testservice;

public class Startup
{
    public Startup(IConfiguration configuration)
    {
        Configuration = configuration;
    }

    public IConfiguration Configuration { get; }

    // This method gets called by the runtime. Use this method to add services to the container.
    public void ConfigureServices(IServiceCollection services)
    {
        services.Configure<DatabaseSettings>(Configuration.GetSection("MongoDB"));

        services.AddControllers();

        services.AddSingleton<RabbitMQService>();

        services.AddSingleton<StorageService>();

        services.AddSingleton<TestCasesService>();

        services.AddSingleton<TestRunsService>();

        services.AddHealthChecks()
            .AddCheck<RabbitMQHealthCheck>("rabbitmq-check");
    }

    // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
    public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
    {
        if (env.IsDevelopment())
        {
            app.UseDeveloperExceptionPage();
        }

        app.UseRouting();

        app.UseAuthorization();

        app.UseEndpoints(endpoints =>
        {
            endpoints.MapControllers();
            endpoints.MapHealthChecks("/healthcheck");
        });

        app.ApplicationServices.GetRequiredService<RabbitMQService>().StartProcessing();
    }
}
