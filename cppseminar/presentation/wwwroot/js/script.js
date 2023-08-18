console.log("This is the start of the script.js...");

const connection = new signalR.HubConnectionBuilder()
    .withUrl("http://localhost:8525/monitor")
    .configureLogging(signalR.LogLevel.Information)
    .build();

async function start() {
    try {
        await connection.start();
        console.log("SignalR Connected.");
    }
    catch (err) {
        console.log(err);
        setTimeout(start, 5000);
    }
};

connection.onclose(async () => {
    console.log("Connection closed.");
    await start();
});

// Define the ReceiveMessage method so that it can be triggered from the Hub
connection.on("ReceiveMessage", (user, message) => {
    console.log("ReceiveMessage():", user, message);
});

async function main() {
    console.log("We are in main.");

    // Start the connection.
    await start();
    
    // Invoke SendMessage on the Hub
    try {
        await connection.invoke("SendMessage", "user123-TODO", "This is a message " + (new Date).getMilliseconds());
    } catch (err) {
        console.error(err);
    }
}

main();