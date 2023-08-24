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
        // console.log(users);
        users.forEach(user => {
            const row = document.getElementById(user.UserEmail)
            const tbl = document.getElementById("userLogs");
            const dateNow = Date.now()
            const timestamp = new Date(user.Timestamp) 
            if (row === null) {
                const temp = `<b><tr id=${user.UserEmail}><td>${user.UserEmail}</td><td>${Math.floor((dateNow - timestamp) / 1000)}</td></tr></b>`;
                tbl.innerHTML += temp;
            }
            else {
                row.innerHTML = `<td> 
                                ${user.UserEmail}
                                </td>
                                <td>
                                ${Math.floor((dateNow - timestamp) / 1000)}
                                </td>`
            }
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

    setInterval(invokeGetConnectedUsersRecentAsync, 1000);
}

main();