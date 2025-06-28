async function runBrowserPingTest() {
    const userType = document.querySelector('input[name="userType"]:checked').value;
    const targets = {
        interpreter: ["216.20.237.2", "216.20.235.2"],
        linc: ["216.20.237.3", "216.20.235.3"]
    }[userType];

    const resultsDiv = document.getElementById('results-log');
    resultsDiv.innerText = "Running 10-minute browser-based ping test...\n\n";

    for (let ip of targets) {
        resultsDiv.innerText += `Pinging ${ip}...\n`;

        let stats = {
            ip,
            sent: 600,
            received: 0,
            times: []
        };

        for (let i = 0; i < stats.sent; i++) {
            const start = performance.now();
            try {
                await fetch(`http://${ip}`, { mode: "no-cors", cache: "no-store" });
                const rtt = performance.now() - start;
                stats.times.push(rtt);
                stats.received++;
            } catch {
                const rtt = performance.now() - start;
                stats.times.push(rtt);
            }
            await new Promise(r => setTimeout(r, 1000));  // 1-second delay
        }

        const loss = stats.sent - stats.received;
        const lossPercent = (loss / stats.sent) * 100;
        const min = Math.min(...stats.times).toFixed(2);
        const max = Math.max(...stats.times).toFixed(2);
        const avg = (stats.times.reduce((a, b) => a + b, 0) / stats.times.length).toFixed(2);

        resultsDiv.innerText += `
Results for ${ip}:
  Packets Sent     : ${stats.sent}
  Replies Received : ${stats.received}
  Packet Loss      : ${loss} (${lossPercent.toFixed(2)}%)
  RTT Min / Max / Avg (ms): ${min} / ${max} / ${avg}
\n----------------------------------------\n`;
    }
}
