console.log("Test", userEmail);

const connection = new signalR.HubConnectionBuilder()
    .withUrl("/monitor")
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

async function invokeSendMessage() {
    // Invoke SendMessage on the Hub
    try {
        await connection.invoke("SendMessage", userEmail, "This is a message " + (new Date).getMilliseconds());
    } catch (err) {
        console.error(err);
    }
    return false;
}

async function main() {
    // Start the connection.
    await start();
}

main();