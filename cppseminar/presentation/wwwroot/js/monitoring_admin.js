const connection = new signalR.HubConnectionBuilder()
    .withUrl("/monitor")
    .configureLogging(signalR.LogLevel.Information)
    .build();

async function start() {
    try {
        await connection.start();
        document.getElementById("alertBox").textContent = "";
        console.log("SignalR Connected.");
    }
    catch (err) {
        console.log(err);
        setTimeout(start, 5000);
    }
};

connection.onclose(async () => {
    console.log("Connection closed.");
    document.getElementById("alertBox").textContent = "Connection closed, trying to start a new connection...";
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
        let time = 0;
        let color = "black";
        users.forEach(user => {
            time = Math.round(user.Timestamp * 100) / 100;
            if (time > 5 && time < 15){
                color = "orange";
            }
            else if (time > 15) {
                color = "red";
            }
            tbl.innerHTML += `<b><tr id=${user.UserEmail}><td>${user.UserEmail}</td><td style="color:${color}">${time} seconds ago</td></tr></b>`;
        })
    }
    catch (exception){
        console.log(exception);
    }
});
connection.on("ErrorGettingUsers", (message)=>{
    const box = document.getElementById("alertBox");
    box.textContent = message;
})

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