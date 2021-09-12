using System;
using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.OpenApi.Models;
using submissions.Data;
using submissions.Services;


namespace submissions
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
            services.AddSwaggerGen(c =>
            {
                c.SwaggerDoc("v1", new OpenApiInfo { Title = "submissions", Version = "v1" });
            });
            services.AddDbContext<CosmosContext>(
                options =>
                {
                    // Read sectionName from file and set cosmos connection
                    // TODO: Rewrite this with IConfiguration.Validate...
                    ICosmosSettings cosmosSettings = new CosmosSettings();
                    string sectionName = nameof(CosmosSettings);
                    var section = Configuration.GetSection(sectionName);
                    if (!section.Exists())
                    {
                        System.Diagnostics.Trace.TraceError("Section for cosmos settings doesn't exist");
                        throw new ArgumentException($"Section {sectionName} doesn't exist, or is empty");
                    }
                    section.Bind(cosmosSettings);
                    Validator.ValidateObject(cosmosSettings, new ValidationContext(cosmosSettings), true);
                    options.UseCosmos(cosmosSettings.ConnectionString, cosmosSettings.DatabaseName);
                    // TODO: Delete
                    //options.LogTo(Console.WriteLine);
                });
            services.AddSingleton<StorageService>();

        }


        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env, CosmosContext cosmosContext)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
                app.UseSwagger();
                app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "submissions v1"));
            }

            app.UseRouting();

            app.UseAuthorization();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers();
            });
            // Custom setup
            cosmosContext.Database.EnsureCreated();
        }
    }
}
