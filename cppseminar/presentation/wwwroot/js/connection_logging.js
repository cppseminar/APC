const connection = new signalR.HubConnectionBuilder()
    .withUrl("/monitor")
    .configureLogging(signalR.LogLevel.Information)
    .build();

connection.onclose(async () => {
    console.log("Connection closed.");
    await start();
});

function setConnectionStatusDisplay(status, color) {
    let elem = document.getElementById("connection-status");
    elem.style.color = color;
    elem.innerText = "Connection status: " + status;
}

function showLastLog() {
    document.getElementById("last-timestamp").innerText = "Last timestamp sent at: " + new Date().toLocaleTimeString();
}

async function mainloop() {
    while (true) {                
        try {
            await connection.invoke("LogConnection");
            showLastLog();
        } catch (err) {
            console.error(err);
            setConnectionStatusDisplay("Error when invoking LogConnection", "red");
            break;
        }
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
}

async function start() {
    try {
        await connection.start();
        console.log("SignalR Connected.");
        setConnectionStatusDisplay("Connected", "green");
        mainloop();
    }
    catch (err) {
        console.log(err);
        setConnectionStatusDisplay("Unable to connect", "red");
        setTimeout(start, 5000);
    }
}

start();