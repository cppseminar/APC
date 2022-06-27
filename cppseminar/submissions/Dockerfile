FROM mcr.microsoft.com/dotnet/aspnet:5.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:5.0 AS build
WORKDIR /src
COPY ["submissions.csproj", "./submissions.csproj"]
RUN dotnet restore "submissions.csproj"
COPY . .
RUN dotnet build "submissions.csproj" -c Release -o /app/build

FROM build as dev
CMD dotnet watch run --urls=http://0.0.0.0:80

FROM build AS publish
RUN dotnet publish "submissions.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "submissions.dll"]
