// dashboard.js
document.addEventListener("DOMContentLoaded", function() {
    const userTable = document.getElementById("user-table");
    const chatTable = document.getElementById("chat-table");

    // Fetch and display users
    fetch("/admin/users")
        .then(response => response.json())
        .then(data => {
            data.users.forEach(user => {
                const row = userTable.insertRow();
                row.insertCell(0).innerText = user.full_name;
                row.insertCell(1).innerText = user.username;
                row.insertCell(2).innerText = user.telegram_id;
                row.insertCell(3).innerText = user.created_at;
            });
        });

    // Fetch and display chat history
    fetch("/admin/chats")
        .then(response => response.json())
        .then(data => {
            data.chats.forEach(chat => {
                const row = chatTable.insertRow();
                row.insertCell(0).innerText = chat.user_full_name;
                row.insertCell(1).innerText = chat.agent_name;
                row.insertCell(2).innerText = chat.start_time;
                row.insertCell(3).innerText = chat.end_time || "Ongoing";
            });
        });
});