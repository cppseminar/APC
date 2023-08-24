console.log("Test", userEmail);

const connection = new signalR.HubConnectionBuilder()
    .withUrl("/monitor")
    .configureLogging(signalR.LogLevel.Information)
    .build();

async function start() {
    try {
        await connection.start();
        console.log("SignalR Connected.");
        setButtonColor("green");
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

function setButtonColor(color) {
    document.getElementById("start-logging-button").style.color = color;
}

function showLastLog() {
    document.getElementById("last-timestamp").innerText = "Last timestamp sent at: " + new Date().toISOString();
}

async function mainloop() {
    if (connection.state === signalR.HubConnectionState.Connected)
        return;

    // Start the connection.
    await start();

    while (true) {
        try {
            await connection.invoke("LogConnection");
            showLastLog();
        } catch (err) {
            console.error(err);
            setButtonColor("red");
            break;
        }
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
}