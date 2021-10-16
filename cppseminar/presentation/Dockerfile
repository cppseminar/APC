#See https://aka.ms/containerfastmode to understand how Visual Studio uses this Dockerfile to build your images for faster debugging.

#
FROM mcr.microsoft.com/dotnet/aspnet:5.0 AS base
#FROM mcr.microsoft.com/dotnet/aspnet:6.0-alpine AS base
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
#ENTRYPOINT ["/tini", "--"]
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:5.0 AS build
#FROM mcr.microsoft.com/dotnet/sdk:6.0-alpine AS build
WORKDIR /src
COPY ["presentation.csproj", "."]
RUN dotnet restore "presentation.csproj"
COPY ["Model", "Model"]
COPY  "Pages" "Pages"
COPY "Services" "Services"
COPY ["Program.cs", "Startup.cs", "appsettings.json", "appsettings.Development.json", "."]

FROM build as dev
EXPOSE 8080
CMD dotnet watch run --urls=http://0.0.0.0:8080

FROM build AS publish
RUN dotnet build "presentation.csproj" -c Release -o /app/build
RUN dotnet publish "presentation.csproj" -c Release -o /app/publish

FROM base AS final
#RUN dotnet build "presentation.csproj" -c Release -o /app/build
WORKDIR /app
COPY --from=publish /app/publish .
CMD ["dotnet", "presentation.dll"]
