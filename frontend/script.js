async function runSpeedTest() {
    const res = await fetch('/speedtest');
    const data = await res.json();
    document.getElementById('results').innerText = JSON.stringify(data, null, 2);
}

async function runPingTest() {
    const userType = document.querySelector('input[name="userType"]:checked').value;
    const res = await fetch('/pingtest', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ userType })
    });
    const data = await res.json();
    document.getElementById('results').innerText = JSON.stringify(data, null, 2);
}

async function sendResults() {
    const email = document.getElementById('email').value;
    const resText = document.getElementById('results').innerText;
    await fetch('/send', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ email, content: resText })
    });
    alert("Email sent!");
}
