async function runSpeedTest() {
    const res = await fetch('/speedtest');
    const text = await res.text();
    try {
        const data = JSON.parse(text);
        document.getElementById('results').innerText = JSON.stringify(data, null, 2);
    } catch (err) {
        document.getElementById('results').innerText = "Speed Test Error:\n" + text;
    }
}

async function runPingTest() {
    const userType = document.querySelector('input[name="userType"]:checked').value;
    const res = await fetch('/pingtest', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ userType })
    });
    const text = await res.text();
    try {
        const data = JSON.parse(text);
        document.getElementById('results').innerText = JSON.stringify(data, null, 2);
    } catch (err) {
        document.getElementById('results').innerText = "Ping Test Error:\n" + text;
    }
}

async function sendResults() {
    const email = document.getElementById('email').value;
    const resText = document.getElementById('results').innerText;
    const res = await fetch('/send', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email, content: resText })
    });
    const text = await res.text();
    try {
        const data = JSON.parse(text);
        alert(data.status === "sent" ? "Email sent!" : "Something went wrong.");
    } catch (err) {
        alert("Send Error:\n" + text);
    }
}
