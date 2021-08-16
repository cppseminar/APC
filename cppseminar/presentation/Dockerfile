#See https://aka.ms/containerfastmode to understand how Visual Studio uses this Dockerfile to build your images for faster debugging.

FROM mcr.microsoft.com/dotnet/aspnet:5.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:5.0 AS build
WORKDIR /src
COPY ["presentation.csproj", "."]
RUN dotnet restore "presentation.csproj"
COPY . .

FROM build as dev
CMD dotnet watch run --urls=http://0.0.0.0:8080

FROM build AS publish
RUN dotnet build "presentation.csproj" -c Release -o /app/build
RUN dotnet publish "presentation.csproj" -c Release -o /app/publish

FROM base AS final
RUN dotnet build "presentation.csproj" -c Release -o /app/build
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "presentation.dll"]