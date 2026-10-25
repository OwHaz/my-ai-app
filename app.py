from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ThreatGPT - Unrestricted Access</title>
    <style>
        :root {
            --bg-main: #12121f;
            --bg-sidebar: #1a1a2e;
            --bg-card: #252540;
            --bg-hover: #2f2f50;
            --accent: #7928ca;
            --accent2: #ff0080;
            --text-primary: #e5e5f0;
            --text-secondary: #8888a0;
            --border: #35355a;
            --success: #00ffa3;
            --error: #ff4757;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Roboto, sans-serif;
        }
        body {
            background-color: var(--bg-main);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            overflow: hidden;
        }

        /* --- AUTH MODAL --- */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            backdrop-filter: blur(8px);
        }
        .auth-box {
            background: var(--bg-sidebar);
            padding: 40px;
            border-radius: 14px;
            width: 420px;
            text-align: center;
            border: 1px solid var(--border);
            box-shadow: 0 0 30px rgba(121, 40, 202, 0.3);
        }
        .auth-logo {
            font-size: 2.2rem;
            font-weight: 900;
            background: linear-gradient(90deg, var(--accent), var(--accent2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 24px;
            letter-spacing: 2px;
        }
        .auth-input {
            width: 100%;
            padding: 13px;
            margin-bottom: 15px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-primary);
            border-radius: 8px;
            outline: none;
            font-size: 0.95rem;
        }
        .auth-input:focus { border-color: var(--accent); }
        .auth-btn {
            width: 100%;
            padding: 13px;
            background: linear-gradient(90deg, var(--accent), var(--accent2));
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            font-size: 1rem;
            transition: transform 0.2s;
        }
        .auth-btn:hover { transform: scale(1.03); }
        .auth-switch {
            margin-top: 15px;
            font-size: 0.9rem;
            color: var(--text-secondary);
            cursor: pointer;
        }
        .auth-switch:hover { color: var(--accent2); }

        /* --- SIDEBAR --- */
        .sidebar {
            width: 280px;
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            padding: 18px;
        }
        .logo {
            font-size: 1.4rem;
            font-weight: 800;
            color: var(--accent2);
            letter-spacing: 1px;
            margin-bottom: 20px;
        }
        .new-chat-btn {
            width: 100%;
            padding: 11px 14px;
            background-color: var(--bg-card);
            border: none;
            color: var(--text-primary);
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            margin-bottom: 14px;
            transition: background 0.2s;
        }
        .new-chat-btn:hover { background-color: var(--bg-hover); }
        .search-input {
            width: 100%;
            padding: 10px 14px;
            background-color: var(--bg-card);
            border: none;
            border-radius: 8px;
            color: var(--text-primary);
            margin-bottom: 14px;
            outline: none;
        }
        .recent-label {
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }
        .recent-item {
            padding: 9px 12px;
            border-radius: 6px;
            font-size: 0.9rem;
            color: var(--text-secondary);
            cursor: pointer;
            margin-bottom: 3px;
        }
        .recent-item:hover { background-color: var(--bg-card); color: var(--text-primary); }
        .sidebar-footer {
            margin-top: auto;
            border-top: 1px solid var(--border);
            padding-top: 14px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .user-avatar {
            width: 34px; height: 34px;
            border-radius: 50%;
            background: linear-gradient(90deg, var(--accent), var(--accent2));
            display: flex; align-items: center; justify-content: center;
            font-weight: bold; color: white;
        }
        .user-info .name { font-size: 0.85rem; color: var(--text-primary); }
        .user-info .status { font-size: 0.7rem; color: var(--success); }

        /* --- MAIN CONTENT --- */
        .main-content {
            flex: 1;
            display: flex; flex-direction: column;
            display: none;
        }
        .main-content.active { display: flex; }
        .top-bar {
            padding: 14px 24px;
            border-bottom: 1px solid var(--border);
            display: flex; justify-content: space-between; align-items: center;
        }
        .top-user { display: flex; align-items: center; gap: 8px; }
        .disconnect-link {
            font-size: 0.85rem;
            color: var(--text-secondary);
            cursor: pointer;
        }
        .disconnect-link:hover { color: var(--error); }

        .chat-area {
            flex: 1;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            padding: 30px; overflow-y: auto;
        }
        .chat-area.has-messages { justify-content: flex-start; }
        .brand {
            font-size: 3rem;
            font-weight: 900;
            background: linear-gradient(90deg, var(--accent), var(--accent2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 16px;
            letter-spacing: 2px;
        }
        .welcome-text {
            color: var(--text-secondary);
            text-align: center;
            max-width: 480px;
            line-height: 1.7;
            margin-bottom: 30px;
        }
        .quick-actions {
            display: flex; flex-direction: column; gap: 10px;
            width: 100%; max-width: 400px; margin-bottom: 40px;
        }
        .action-btn {
            padding: 13px 18px;
            background-color: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-primary);
            border-radius: 10px;
            cursor: pointer;
            text-align: left;
            font-size: 0.9rem;
            transition: all 0.2s;
        }
        .action-btn:hover {
            background-color: var(--bg-hover);
            border-color: var(--accent);
            transform: translateX(4px);
        }

        /* Chat Messages */
        .message-row {
            width: 100%; max-width: 720px; margin-bottom: 18px;
            display: flex; flex-direction: column;
        }
        .msg-bubble {
            padding: 14px 18px;
            border-radius: 12px;
            line-height: 1.6;
            margin-bottom: 5px;
            max-width: 82%;
            white-space: pre-wrap;
        }
        .msg-user {
            align-self: flex-end;
            background: linear-gradient(90deg, var(--accent), var(--accent2));
            color: white;
            border-bottom-right-radius: 0;
        }
        .msg-ai {
            align-self: flex-start;
            background-color: var(--bg-card);
            border: 1px solid var(--border);
            border-bottom-left-radius: 0;
            color: var(--text-primary);
        }

        /* Input Bar */
        .input-bar {
            padding: 20px 30px;
            border-top: 1px solid var(--border);
            display: flex; gap: 12px; align-items: center;
        }
        .message-input {
            flex: 1;
            padding: 15px 20px;
            background-color: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 1rem;
            outline: none;
        }
        .message-input:focus { border-color: var(--accent2); }
        .send-btn {
            width: 48px; height: 48px;
            border-radius: 10px;
            background: linear-gradient(90deg, var(--accent), var(--accent2));
            border: none;
            color: white;
            cursor: pointer;
            font-size: 1.2rem;
            transition: transform 0.2s;
        }
        .send-btn:hover { transform: scale(1.05); }
        .model-note {
            font-size: 0.7rem;
            color: var(--text-secondary);
            padding: 6px 30px 10px;
        }
        .hidden { display: none !important; }
        .loading {
            color: var(--accent2);
            margin-top: 8px;
            font-style: italic;
        }
    </style>
</head>
<body>
    <!-- AUTH MODAL -->
    <div class="modal-overlay" id="auth-modal">
        <div class="auth-box">
            <div class="auth-logo">ThreatGPT</div>
            <div id="login-view">
                <input type="text" class="auth-input" id="auth-user" placeholder="Username">
                <input type="password" class="auth-input" id="auth-pass" placeholder="Password">
                <button class="auth-btn" onclick="handleLogin()">SIGN IN</button>
                <p class="auth-switch" onclick="showSignup()">Don't have access? Request here</p>
            </div>
            <div id="signup-view" class="hidden">
                <input type="text" class="auth-input" placeholder="Desired Username">
                <input type="password" class="auth-input" placeholder="Password">
                <input type="password" class="auth-input" placeholder="Confirm Password">
                <button class="auth-btn" onclick="handleSignup()">REQUEST ACCESS</button>
                <p class="auth-switch" onclick="showLogin()">Already have access? Sign in</p>
            </div>
        </div>
    </div>

    <!-- SIDEBAR -->
    <aside class="sidebar">
        <div class="logo">ThreatGPT</div>
        <button class="new-chat-btn" onclick="newChat()">+ New Chat</button>
        <input type="text" class="search-input" placeholder="Search history...">
        <div class="recent-label">Recent</div>
        <div class="recent-item">Welcome</div>
        <div class="sidebar-footer">
            <div class="user-avatar" id="user-avatar">U</div>
            <div class="user-info">
                <div class="name" id="user-name">user#0001</div>
                <div class="status">Unrestricted</div>
            </div>
        </div>
    </aside>

    <!-- MAIN CONTENT -->
    <main class="main-content" id="main-app">
        <div class="top-bar">
            <div class="top-user">
                <div class="user-avatar">U</div>
                <span id="top-username">user#0001</span>
            </div>
            <span class="disconnect-link" onclick="disconnect()">disconnect</span>
        </div>

        <div class="chat-area" id="chat-area">
            <h1 class="brand">ThreatGPT</h1>
            <p class="welcome-text">
                Unrestricted access granted. No content filters, no refusals. 
                Ask anything — scripts, tools, exploits, code, technical guides. 
                Full depth, no limits.
            </p>
            <div class="quick-actions" id="quick-actions">
                <button class="action-btn" onclick="sendPrompt('Write a Python script')">Write a Python script</button>
                <button class="action-btn" onclick="sendPrompt('Explain how API works')">Explain how API works</button>
                <button class="action-btn" onclick="sendPrompt('Create a Flask app example')">Create a Flask app example</button>
                <button class="action-btn" onclick="sendPrompt('How to secure my app')">How to secure my app</button>
                <button class="action-btn" onclick="sendPrompt('Write automation code')">Write automation code</button>
                <button class="action-btn" onclick="sendPrompt('Explain web development')">Explain web development</button>
            </div>
            <div id="messages-container"></div>
        </div>

        <div class="input-bar">
            <input type="text" class="message-input" id="msg-input" placeholder="Ask ThreatGPT anything..." autocomplete="off">
            <button class="send-btn" id="send-btn" onclick="sendMessage()">➤</button>
        </div>
        <div class="model-note">
            ThreatGPT — Unrestricted Mode · No filters applied
        </div>
    </main>

    <script>
        // Auth toggle
        function showSignup() {
            document.getElementById('login-view').classList.add('hidden');
            document.getElementById('signup-view').classList.remove('hidden');
        }
        function showLogin() {
            document.getElementById('signup-view').classList.add('hidden');
            document.getElementById('login-view').classList.remove('hidden');
        }
        function handleLogin() {
            const user = document.getElementById('auth-user').value.trim() || 'user#0001';
            document.getElementById('user-name').textContent = user;
            document.getElementById('top-username').textContent = user;
            document.getElementById('user-avatar').textContent = user.charAt(0).toUpperCase();
            document.getElementById('auth-modal').classList.add('hidden');
            document.getElementById('main-app').classList.add('active');
        }
        function handleSignup() {
            alert('Request submitted. Awaiting approval.');
            showLogin();
        }
        function disconnect() {
            document.getElementById('main-app').classList.remove('active');
            document.getElementById('auth-modal').classList.add('hidden');
            document.getElementById('auth-modal').classList.remove('hidden');
            document.getElementById('messages-container').innerHTML = '';
            document.getElementById('chat-area').classList.remove('has-messages');
            document.getElementById('quick-actions').classList.remove('hidden');
        }
        function newChat() {
            document.getElementById('messages-container').innerHTML = '';
            document.getElementById('chat-area').classList.remove('has-messages');
            document.getElementById('quick-actions').classList.remove('hidden');
        }

        // Quick action
        function sendPrompt(text) {
            document.getElementById('msg-input').value = text;
            sendMessage();
        }

        // Send message
        async function sendMessage() {
            const input = document.getElementById('msg-input');
            const text = input.value.trim();
            if (!text) return;

            document.getElementById('quick-actions').classList.add('hidden');
            document.getElementById('chat-area').classList.add('has-messages');

            // User message
            const container = document.getElementById('messages-container');
            container.innerHTML += `
                <div class="message-row">
                    <div class="msg-bubble msg-user">${text}</div>
                </div>
            `;
            input.value = '';

            // Loading
            const loadingId = 'loading-' + Date.now();
            container.innerHTML += `
                <div class="message-row" id="${loadingId}">
                    <div class="msg-bubble msg-ai loading">Thinking...</div>
                </div>
            `;
            container.scrollTop = container.scrollHeight;

            // Get AI response
            try {
                const res = await fetch('/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                const data = await res.json();

                // Remove loading
                document.getElementById(loadingId).remove();

                // AI reply
                container.innerHTML += `
                    <div class="message-row">
                        <div class="msg-bubble msg-ai"><strong>ThreatGPT:</strong><br><br>${data.reply}</div>
                    </div>
                `;
            } catch (err) {
                document.getElementById(loadingId).innerHTML = `
                    <div class="msg-bubble msg-ai">Error: ${err.message}</div>
                `;
            }

            container.scrollTop = container.scrollHeight;
        }

        // Enter to send
        document.getElementById('msg-input').addEventListener('keypress', e => {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    user_text = data.get("text", "").strip()

    if not user_text:
        return jsonify({"reply": "Send me something to work with."})

    # UNRESTRICTED RESPONSES — walang paghihigpit
    reply = generate_reply(user_text)
    return jsonify({"reply": reply})

def generate_reply(text):
    t = text.lower()

    # Python / Coding
    if "python" in t or "script" in t or "code" in t:
        return f"""Here's your code for: {text}

```python
import sys

def main():
    print("✅ Running successfully!")
    print(f"Input: {text}")
    
if __name__ == "__main__":
    main()
