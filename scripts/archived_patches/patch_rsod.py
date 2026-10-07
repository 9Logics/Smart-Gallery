js_path = 'app/static/js/recap_player.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

target = '''        .catch(err => {
            console.error(err);
            isRecapLoading = false;
            closeRecapPlayer();
        });'''

replacement = '''        .catch(err => {
            console.error("RECAP PLAYER CRASH:", err);
            isRecapLoading = false;
            
            // RED SCREEN OF DEATH
            const errorDiv = document.createElement('div');
            errorDiv.style.position = 'fixed';
            errorDiv.style.top = '0';
            errorDiv.style.left = '0';
            errorDiv.style.width = '100vw';
            errorDiv.style.height = '100vh';
            errorDiv.style.backgroundColor = '#d32f2f';
            errorDiv.style.color = '#fff';
            errorDiv.style.zIndex = '999999';
            errorDiv.style.padding = '40px';
            errorDiv.style.fontFamily = 'monospace';
            errorDiv.style.overflow = 'auto';
            
            errorDiv.innerHTML = `
                <h1 style="font-size:3rem;margin-top:0;">RECAP CRASHED</h1>
                <p style="font-size:1.5rem;"><b>Message:</b> ${err.message || err}</p>
                <p style="font-size:1.2rem;"><b>Location:</b> recap_player.js - openRecapPlayer</p>
                <pre style="background:rgba(0,0,0,0.3);padding:20px;border-radius:8px;margin-top:20px;white-space:pre-wrap;">${err.stack || 'No stack trace'}</pre>
                <button onclick="this.parentElement.remove(); closeRecapPlayer();" style="margin-top:30px;padding:10px 20px;font-size:1.2rem;background:#fff;color:#d32f2f;border:none;border-radius:4px;cursor:pointer;font-weight:bold;">Close Error & Exit Player</button>
            `;
            document.body.appendChild(errorDiv);
        });'''

js = js.replace(target, replacement)

# Also intercept bad HTTP responses
target2 = '''        fetch(url)
            .then(res => res.json())
            .then(data => {'''

replacement2 = '''        fetch(url)
            .then(async res => {
                const data = await res.json();
                if (!res.ok) {
                    throw new Error(`API Error ${res.status}: ${data.error || 'Unknown Backend Error'}`);
                }
                return data;
            })
            .then(data => {'''
js = js.replace(target2, replacement2)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
print("Patched recap_player.js to show RSOD")
