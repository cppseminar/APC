FROM mcr.microsoft.com/dotnet/aspnet:6.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /src
COPY ["monitoringservice.csproj", "./monitoringservice.csproj"]
RUN dotnet restore "monitoringservice.csproj"
COPY . .
RUN dotnet build "monitoringservice.csproj" -c Release -o /app/build

FROM build as dev
CMD dotnet watch run --urls=http://0.0.0.0:80

FROM build AS publish
RUN dotnet publish "monitoringservice.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "monitoringservice.dll"]
