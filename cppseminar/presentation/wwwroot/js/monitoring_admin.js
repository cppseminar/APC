// setInterval(()=>{
//     var response = fetch("http://localhost:8080/monitoring/getUsers")
// },5000)
const connection = new signalR.HubConnectionBuilder()
    .withUrl("/monitor")
    .configureLogging(signalR.LogLevel.Information)
    .build();

async function start() {
    try {
        await connection.start();
        console.log("SignalR Connected.");
        //setInterval(invokeSendMessage, 10000);
        invokeSendMessage();
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
connection.on("ReceiveUsers", (users, message) => {
    console.log(users)
    // users.forEach(user => {
    //     const row = document.getElementById(user.email)
    //     const tbl = document.getElementById("userLogs");
    //     if (row === null){
    //         const dateNow = Date.now()
    //         const timestamp = new Date(user.timestamp) 
    //         tbl.innerHTML += `<tr id="${user.email}">
    //         <td>
    //             ${user.email}
    //         </td>
    //         <td>
    //             ${Math.floor((dateNow - timestamp) / 1000)}
    //         </td>
    //     </tr>`
    //     }
    //     else{
    //         row.innerHTML = `<td> 
    //                         ${user.email}
    //                         </td>
    //                         <td>
    //                         ${Math.floor((dateNow - timestamp) / 1000)}
    //                         </td>`
    //     }
    //     console.log(user.email);
    //     console.log(user.timestamp);
    // })
});

async function invokeSendMessage() {
    // Invoke SendMessage on the Hub
    try {
        await connection.invoke("GetConnectedUsersRecentAsync");
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