FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["presentation.csproj", "./presentation.csproj"]
RUN dotnet restore "presentation.csproj"
COPY . .
RUN dotnet build "presentation.csproj" -c Release -o /app/build

FROM build as dev
EXPOSE 8080
CMD dotnet watch run --urls=http://0.0.0.0:8080

FROM build AS publish
RUN dotnet publish "presentation.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "presentation.dll"]
