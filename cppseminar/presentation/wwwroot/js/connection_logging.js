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
    // Start the connection.
    await start();

    let counter = 0;
    while (true) {
        try {
            console.log(counter, "invoking LogConnection...");
            await connection.invoke("LogConnection");
            counter += 1;
            showLastLog();
        } catch (err) {
            console.error(err);
            setButtonColor("red");
            break;
        }
        await new Promise(resolve => setTimeout(resolve, 2000));
    }
}