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
connection.on("ReceiveUsers", (users) => {
    try {
        users = JSON.parse(users);
        const tbl = document.getElementById("userLogs");
        tbl.innerHTML = `<tr>
                        <th>
                            User email
                        </th>
                        <th>
                            Last message 
                        </th>
                        </tr>`;
        users.forEach(user => {
            tbl.innerHTML += `<b><tr id=${user.UserEmail}><td>${user.UserEmail}</td><td>${Math.round(user.Timestamp * 100) / 100
        } seconds ago</td></tr></b>`;
        })
    }
    catch (exception){
        console.log(exception);
    }
});

async function invokeGetConnectedUsersRecentAsync() {
    // Invoke SendMessage on the Hub
    try {
        await connection.invoke("GetConnectedUsersRecentAsync");
    } catch (err) {
        console.error(err);
    }
}

async function main() {
    // Start the connection.
    await start();

    setInterval(invokeGetConnectedUsersRecentAsync, 2000);
}

main();