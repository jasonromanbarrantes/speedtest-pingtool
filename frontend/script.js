async function runSpeedTest() {
    document.getElementById('results').innerText = "Running speed tests...";
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
    document.getElementById('results').innerText = "Starting 10-minute ping test...";

    const userType = document.querySelector('input[name="userType"]:checked').value;
    const res = await fetch('/pingtest', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ userType })
    });

    const { test_id } = await res.json();
    document.getElementById('results').innerText = "Running...\nTest ID: " + test_id;

    const pollStatus = async () => {
        const statusRes = await fetch(`/ping-status/${test_id}`);
        const data = await statusRes.json();

        if (data.status === "running") {
            setTimeout(pollStatus, 15000);  // poll again in 15 sec
        } else {
            document.getElementById('results').innerText = JSON.stringify(data, null, 2);
        }
    };

    setTimeout(pollStatus, 15000);  // start polling after delay
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
