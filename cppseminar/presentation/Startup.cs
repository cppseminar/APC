using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authentication.Google;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.HttpOverrides;
using Microsoft.Azure.Storage.Blob;
using Microsoft.Azure.Storage;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using System;

using presentation.Services;

namespace presentation
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        public void ConfigureServices(IServiceCollection services)
        {
            services.AddRazorPages(opts => {
                opts.Conventions.AuthorizeFolder("/Admin", "Administrator");
            });
            services.Configure<Microsoft.AspNetCore.Routing.RouteOptions>(options =>
            {
                options.AppendTrailingSlash = true;
                options.LowercaseUrls = true;
            });
            services.Configure<ForwardedHeadersOptions>(options =>
            {
                options.ForwardedHeaders =
                    ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto | ForwardedHeaders.XForwardedHost;
                options.KnownNetworks.Clear();
                options.KnownProxies.Clear();
            });
            services.AddSingleton<SubmissionService>();
            services.AddSingleton<TaskService>();
            services.AddSingleton<UserService>();
            services.AddSingleton<AuthenticationService>();
            services.AddSingleton<TestCaseService>();
            services.AddSingleton<TestService>();
            services.AddSingleton<IAuthorizationHandler, AdminAuthorizationService>();
            services.AddSingleton<IAuthorizationHandler, TaskAuthorizationService>();
            services.AddSingleton<IAuthorizationHandler, TestCaseAuthorizationService>();

            services.AddHttpContextAccessor();

            // TODO: Review lifetime of cookies
            services.AddAuthentication(options =>
            {
                options.DefaultScheme = CookieAuthenticationDefaults.AuthenticationScheme;
                options.DefaultChallengeScheme = GoogleDefaults.AuthenticationScheme;
            }).AddCookie().AddGoogle(options =>
            {
                IConfigurationSection googleAuthNSection = Configuration.GetSection("GoogleOid");
                options.ClientId = googleAuthNSection["ClientId"];
                options.ClientSecret = googleAuthNSection["ClientSecret"];
                AuthenticationService authInstance = new(Configuration);
                options.Events.OnCreatingTicket = context => AuthenticationService.OnCreateTicketAsync(authInstance, context);
            });

            if (CloudStorageAccount.TryParse(Configuration["STORAGE_CONNECTION_STRING"], out CloudStorageAccount keyStorageAccount))
            {
                CloudBlobClient blobClient = keyStorageAccount.CreateCloudBlobClient();
                CloudBlobContainer blobContainer = blobClient.GetContainerReference("cookiekeys");
                blobContainer.CreateIfNotExists();
                services.AddDataProtection().PersistKeysToAzureBlobStorage(blobContainer, "keys.xml");
                // TODO: SetApplicationName
            }
            else
            {
                throw new ArgumentException("Cannot parse connection string to key storage");
            }

            services.AddAuthorization(options => {
                options.FallbackPolicy = new AuthorizationPolicyBuilder().RequireAuthenticatedUser()
                                                                         .Build();
                options.AddPolicy("Administrator", policy => policy.RequireClaim("isAdmin", "true"));
            });
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            app.UseForwardedHeaders();
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }

            app.UseRouting();
            app.UseAuthentication();
            app.UseAuthorization();
            app.UseEndpoints(endpoints =>
            {
                endpoints.MapRazorPages();
            });
        }
    }
}
