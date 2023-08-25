const connection = new signalR.HubConnectionBuilder()
    .withUrl("/monitor")
    .configureLogging(signalR.LogLevel.Information)
    .build();


connection.onclose(async () => {
    console.log("Connection closed.");
    setAlert("Connection closed, trying to start a new connection...");
    await start();
});
function setAlert(message){
    document.getElementById("alertBox").textcontent = message;
}

// Define the ReceiveMessage method so that it can be triggered from the Hub
connection.on("ReceiveUsers", (users) => {
    console.log("Receive users");
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
async function start() {
    try {
        await connection.start();
        document.getElementById("alertBox").textContent = "";
        mainloop();
    }
    catch (err) {
        console.log(err);
        setAlert("Unable to connect.");
        setTimeout(start, 5000);
    }
}

async function mainloop() {
    console.log("Sme po starte");

    while (true){
        try{
            await connection.invoke("GetConnectedUsersRecentAsync");
            await new Promise(resolve => setTimeout(resolve, 2000));
            console.log("Cau");
        }
        catch (err){
            setAlert("Error when invoking GetconnectedUsers");
            break;
        }
    }

}

start();