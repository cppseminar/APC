using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.EntityFrameworkCore;
using testservice.Services;

namespace testservice
{
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
            services.AddControllers();
            services.AddDbContext<DbService>(options =>
            {
                options.UseCosmos(
                    Configuration["COSMOS_CONNECTION_STRING"],
                    Configuration["COSMOS_DB_NAME"]);
            });
            services.AddSingleton<RabbitMQService>();
            services.AddSingleton<StorageService>();
            services.AddHealthChecks()
                .AddCheck<RabbitMQHealthCheck>("rabbitmq-check")
                .AddCheck<CosmosHealthCheck>("cosmos-check");
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env, DbService dbService)
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
            dbService.Database.EnsureCreated();
            app.ApplicationServices.GetRequiredService<RabbitMQService>().StartProcessing();
        }
    }
}
