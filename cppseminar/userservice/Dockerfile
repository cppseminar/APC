FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["userservice.csproj", "./userservice.csproj"]
RUN dotnet restore "userservice.csproj"
COPY . .
RUN dotnet build "userservice.csproj" -c Release -o /app/build

FROM build as dev
CMD dotnet watch run --urls=http://0.0.0.0:80

FROM build AS publish
RUN dotnet publish "userservice.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "userservice.dll"]
