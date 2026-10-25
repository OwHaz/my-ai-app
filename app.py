from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ThreatGPT</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
        body {
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3c 50%, #0f0f23 100%);
            min-height: 100vh;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            width: 100%;
            max-width: 650px;
        }
        .header {
            text-align: center;
            margin-bottom: 35px;
        }
        .logo {
            font-size: 2.8rem;
            font-weight: 900;
            background: linear-gradient(90deg, #ff2e63, #00d9ff, #ff2e63);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shine 3s linear infinite;
            letter-spacing: 2px;
        }
        @keyframes shine { to { background-position: 200% center; } }
        .tagline { color: #9ca3af; margin-top: 8px; font-size: 1rem; }
        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 30px;
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        textarea {
            width: 100%;
            height: 120px;
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 15px;
            color: #fff;
            font-size: 1rem;
            resize: none;
            outline: none;
            transition: border 0.3s;
        }
        textarea:focus { border-color: #00d9ff; }
        button {
            width: 100%;
            padding: 14px;
            margin-top: 15px;
            background: linear-gradient(90deg, #ff2e63, #00d9ff);
            border: none;
            border-radius: 10px;
            color: #fff;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.3s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 217, 255, 0.3);
        }
        button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .result {
            margin-top: 25px;
            padding: 20px;
            background: rgba(0, 217, 255, 0.08);
            border-radius: 10px;
            border-left: 3px solid #00d9ff;
            display: none;
        }
        .result.show { display: block; animation: fadeIn 0.4s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
        .stat { margin: 8px 0; color: #d1d5db; font-size: 0.95rem; }
        .stat strong { color: #00d9ff; }
        .loading { display: none; text-align: center; margin-top: 15px; color: #00d9ff; }
        .loading.show { display: block; }
        .spinner {
            display: inline-block;
            width: 20px; height: 20px;
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-top-color: #00d9ff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
            vertical-align: middle;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="logo">ThreatGPT</h1>
            <p class="tagline">Advanced AI Assistant</p>
        </div>
        <div class="card">
            <textarea id="inputText" placeholder="Ilagay ang iyong mensahe dito..."></textarea>
            <button id="sendBtn" onclick="sendMessage()">Ipadala</button>
            <div class="loading" id="loading">
                <span class="spinner"></span>Pinoproseso...
            </div>
            <div class="result" id="result">
                <p class="stat">✅ <strong>Sagot:</strong> <span id="resMsg"></span></p>
                <p class="stat">📝 <strong>Teksto:</strong> <span id="resText"></span></p>
                <p class="stat">🔤 <strong>Bilang ng Salita:</strong> <span id="resWords"></span></p>
                <p class="stat">📏 <strong>Haba:</strong> <span id="resLen"></span></p>
            </div>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const text = document.getElementById('inputText').value.trim();
            if (!text) { alert('Ilagay muna ang mensahe!'); return; }

            const btn = document.getElementById('sendBtn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');

            btn.disabled = true;
            loading.classList.add('show');
            result.classList.remove('show');

            try {
                const res = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                const data = await res.json();
                
                document.getElementById('resMsg').textContent = data.message;
                document.getElementById('resText').textContent = data.text;
                document.getElementById('resWords').textContent = data.bilang_ng_salitang;
                document.getElementById('resLen').textContent = data.haba_ng_teksto;
                
                result.classList.add('show');
            } catch (err) {
                alert('May naganap na error: ' + err);
            } finally {
                btn.disabled = false;
                loading.classList.remove('show');
            }
        }

        document.getElementById('inputText').addEventListener('keydown', e => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        text = request.args.get("text", "")
        if not text:
            return jsonify({"error": "Ilagay ang ?text=IyongMensahe"}), 400
    else:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Kailangan ng 'text'"}), 400
        text = data["text"]

    return jsonify({
        "message": "Natanggap na ang mensahe!",
        "text": text,
        "bilang_ng_salitang": len(text.split()),
        "haba_ng_teksto": len(text)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
