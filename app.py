from flask import Flask, request, render_template_string, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# === CONFIGURATION ===
WEBHOOK_URL = "https://discord.com/api/webhooks/1564010767869550652/fyB2TqnwwKN8worOu5cQgE2TqL3FVNFPgBFAQBM4VL6iEYJ1kI83kjCcrOVnKtCGWyV6"
OWNER_EMAIL = "blahlhamara@gmail.com"
TRIAL_MESSAGE_LIMIT = 3

users = {}

def send_webhook_log(title, details, color=0x7928ca):
    if not WEBHOOK_URL or WEBHOOK_URL.startswith("ILAGAY"):
        return
    try:
        embed = {
            "title": title,
            "color": color,
            "fields": [{"name": k, "value": str(v), "inline": True} for k, v in details.items()],
            "timestamp": datetime.utcnow().isoformat()
        }
        requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=5)
    except Exception:
        pass

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ThreatGPT</title>
    <style>
        :root {
            --bg-main: #2b2b2b;
            --bg-sidebar: #333333;
            --bg-card: #3c3c3c;
            --bg-hover: #484848;
            --accent: #7928ca;
            --accent2: #ff0080;
            --text-primary: #e0e0e0;
            --text-secondary: #999999;
            --border: #4a4a4a;
            --success: #4cd137;
            --warning: #fbc531;
            --danger: #e84118;
        }
        * {margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',Roboto,sans-serif;}
        body {background:var(--bg-main);color:var(--text-primary);height:100vh;display:flex;overflow:hidden;}
        .hidden {display:none !important;}
        .modal-overlay {position:fixed;inset:0;background:rgba(0,0,0,0.85);display:flex;justify-content:center;align-items:center;z-index:1000;backdrop-filter:blur(6px);}
        .modal-box {background:var(--bg-sidebar);padding:28px;border-radius:12px;border:1px solid var(--border);box-shadow:0 8px 24px rgba(0,0,0,0.4);max-width:420px;width:90%;}
        .modal-title {font-size:1.4rem;font-weight:700;margin-bottom:18px;text-align:center;}
        .auth-box .modal-title {background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
        .modal-input {width:100%;padding:12px;margin-bottom:12px;background:var(--bg-card);border:1px solid var(--border);color:var(--text-primary);border-radius:6px;outline:none;}
        .modal-input:focus {border-color:var(--accent);}
        .btn {width:100%;padding:12px;border:none;border-radius:6px;font-weight:bold;cursor:pointer;transition:transform 0.2s;}
        .btn:hover {transform:scale(1.02);}
        .btn-primary {background:linear-gradient(90deg,var(--accent),var(--accent2));color:#fff;}
        .btn-secondary {background:var(--bg-card);color:var(--text-primary);border:1px solid var(--border);margin-top:8px;}
        .btn-success {background:var(--success);color:#111;}
        .switch-text {margin-top:12px;text-align:center;font-size:0.85rem;color:var(--text-secondary);cursor:pointer;}
        .switch-text:hover {color:var(--accent2);}
        .sub-card {background:var(--bg-card);padding:16px;border-radius:8px;border:1px solid var(--border);margin-bottom:12px;cursor:pointer;transition:all 0.2s;}
        .sub-card:hover {border-color:var(--accent);transform:translateY(-2px);}
        .sub-card.selected {border-color:var(--accent);box-shadow:0 0 0 2px var(--accent);}
        .sub-title {font-weight:bold;font-size:1.1rem;margin-bottom:4px;}
        .sub-price {color:var(--accent2);font-weight:bold;margin-bottom:8px;}
        .sub-desc {font-size:0.85rem;color:var(--text-secondary);}
        .discord-link {display:block;text-align:center;margin-top:16px;color:var(--accent);text-decoration:none;font-weight:bold;}
        .discord-link:hover {color:var(--accent2);}
        .sidebar {width:260px;background:var(--bg-sidebar);border-right:1px solid var(--border);display:flex;flex-direction:column;padding:16px;}
        .logo {font-size:1.25rem;font-weight:700;color:var(--accent2);margin-bottom:16px;}
        .new-chat-btn {width:100%;padding:10px;background:var(--bg-card);border:none;color:var(--text-primary);border-radius:6px;cursor:pointer;margin-bottom:12px;transition:background 0.2s;}
        .new-chat-btn:hover {background:var(--bg-hover);}
        .search-input {width:100%;padding:9px 12px;background:var(--bg-card);border:none;border-radius:6px;color:var(--text-primary);margin-bottom:12px;outline:none;}
        .history-list {flex:1;overflow-y:auto;}
        .history-item {padding:10px 12px;border-radius:6px;font-size:0.9rem;color:var(--text-secondary);cursor:pointer;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
        .history-item:hover, .history-item.active {background:var(--bg-card);color:var(--text-primary);}
        .sidebar-footer {border-top:1px solid var(--border);padding-top:12px;display:flex;align-items:center;gap:10px;margin-top:12px;}
        .user-avatar {width:32px;height:32px;border-radius:50%;background:linear-gradient(90deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-weight:bold;color:#fff;}
        .user-info .name {font-size:0.85rem;color:var(--text-primary);}
        .user-info .status {font-size:0.7rem;}
        .status.trial {color:var(--warning);}
        .status.premium {color:var(--success);}
        .trial-count {font-size:0.75rem;color:var(--warning);margin-top:4px;}
        .main-content {flex:1;display:flex;flex-direction:column;display:none;}
        .main-content.active {display:flex;}
        .top-bar {padding:12px 24px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;}
        .top-user {display:flex;align-items:center;gap:8px;}
        .disconnect-link {font-size:0.85rem;color:var(--text-secondary);cursor:pointer;}
        .disconnect-link:hover {color:var(--danger);}
        .chat-area {flex:1;display:flex;flex-direction:column;padding:24px;overflow-y:auto;gap:16px;}
        .welcome {text-align:center;padding:20px 0;}
        .welcome h1 {font-size:2rem;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px;}
        .welcome p {color:var(--text-secondary);max-width:480px;margin:0 auto 20px;}
        .quick-actions {display:flex;flex-wrap:wrap;gap:8px;justify-content:center;max-width:500px;margin:0 auto;}
        .action-btn {padding:10px 14px;background:var(--bg-card);border:1px solid var(--border);color:var(--text-primary);border-radius:8px;cursor:pointer;font-size:0.9rem;transition:all 0.2s;}
        .action-btn:hover {background:var(--bg-hover);border-color:var(--accent);}
        .msg-row {display:flex;margin-bottom:4px;}
        .msg-row.user {justify-content:flex-end;}
        .msg-row.assistant {justify-content:flex-start;}
        .msg-bubble {max-width:75%;padding:14px 18px;border-radius:12px;line-height:1.6;}
        .msg-row.user .msg-bubble {background:linear-gradient(90deg,var(--accent),var(--accent2));color:#fff;border-bottom-right-radius:4px;}
        .msg-row.assistant .msg-bubble {background:var(--bg-card);border:1px solid var(--border);border-bottom-left-radius:4px;}
        .code-wrap {margin:10px 0;background:#1e1e1e;border-radius:8px;overflow:hidden;}
        .code-header {display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:#252525;border-bottom:1px solid #333;}
        .copy-btn {padding:4px 10px;background:var(--accent);color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.8rem;}
        .copy-btn.copied {background:var(--success);}
        pre {padding:14px;overflow-x:auto;font-family:'Consolas',monospace;font-size:0.9rem;line-height:1.5;}
        code {color:#a5d6ff;}
        .html-preview {margin:10px 0;border:1px solid var(--border);border-radius:8px;overflow:hidden;}
        .preview-header {padding:8px 14px;background:var(--bg-card);border-bottom:1px solid var(--border);font-weight:bold;}
        .preview-frame {width:100%;height:300px;border:none;background:#fff;}
        .uploaded-img {max-width:300px;border-radius:8px;margin:8px 0;}
        .file-attach {display:flex;align-items:center;gap:8px;padding:8px 12px;background:var(--bg-card);border-radius:6px;margin:8px 0;}
        .input-bar {padding:16px 24px;border-top:1px solid var(--border);display:flex;gap:10px;align-items:flex-end;}
        .attach-btn {padding:10px;background:var(--bg-card);border:none;border-radius:6px;color:var(--text-primary);cursor:pointer;font-size:1.1rem;}
        .attach-btn:hover {background:var(--bg-hover);}
        .input-wrapper {flex:1;display:flex;flex-direction:column;gap:6px;}
        .preview-names {display:flex;flex-wrap:wrap;gap:6px;}
        .file-tag {padding:4px 10px;background:var(--bg-card);border-radius:4px;font-size:0.8rem;display:flex;align-items:center;gap:6px;}
        .file-tag button {background:none;border:none;color:var(--danger);cursor:pointer;font-weight:bold;}
        .message-input {width:100%;padding:12px 16px;background:var(--bg-card);border:1px solid var(--border);border-radius:10px;color:var(--text-primary);font-size:0.95rem;outline:none;resize:none;min-height:44px;max-height:120px;}
        .message-input:focus {border-color:var(--accent2);}
        .send-btn {width:44px;height:44px;border-radius:10px;background:linear-gradient(90deg,var(--accent),var(--accent2));border:none;color:#fff;cursor:pointer;font-size:1rem;}
        .send-btn:disabled {opacity:0.4;cursor:not-allowed;}
        .loading {color:var(--accent2);font-style:italic;}
    </style>
</head>
<body>
    <div class="modal-overlay" id="auth-modal">
        <div class="modal-box auth-box">
            <div class="modal-title">ThreatGPT</div>
            <div id="login-view">
                <input type="email" class="modal-input" id="auth-email" placeholder="Enter your Gmail">
                <input type="password" class="modal-input" id="auth-pass" placeholder="Password">
                <button class="btn btn-primary" onclick="handleLogin()">SIGN IN</button>
                <p class="switch-text" onclick="showSignup()">Don't have account? Sign up</p>
            </div>
            <div id="signup-view" class="hidden">
                <input type="email" class="modal-input" id="su-email" placeholder="Your Gmail">
                <input type="password" class="modal-input" id="su-pass" placeholder="Password">
                <input type="password" class="modal-input" id="su-pass2" placeholder="Confirm Password">
                <button class="btn btn-primary" onclick="handleSignup()">SIGN UP</button>
                <p class="switch-text" onclick="showLogin()">Already have account? Sign in</p>
            </div>
        </div>
    </div>

    <div class="modal-overlay hidden" id="sub-modal">
        <div class="modal-box">
            <div class="modal-title">Subscription Required</div>
            <p style="text-align:center;color:var(--text-secondary);margin-bottom:18px;">You've used all your free messages! Upgrade to continue.</p>
            <div class="sub-card" data-plan="monthly" onclick="selectPlan('monthly')">
                <div class="sub-title">Monthly</div>
                <div class="sub-price">₱99 / month</div>
                <div class="sub-desc">Unlimited chat, priority support, all features</div>
            </div>
            <div class="sub-card" data-plan="lifetime" onclick="selectPlan('lifetime')">
                <div class="sub-title">Lifetime 👑</div>
                <div class="sub-price">₱499 — One Time</div>
                <div class="sub-desc">Forever access, no recurring fees, all future updates</div>
            </div>
            <a class="discord-link" href="https://discord.gg/ILAGAY-MO-ANG-SERVER-MO" target="_blank">📢 Join Discord — Pinoy Community</a>
            <button class="btn btn-primary" style="margin-top:18px;" onclick="submitPurchase()">Avail Now</button>
            <button class="btn btn-secondary" onclick="closeSubModal()">Later</button>
        </div>
    </div>

    <div class="modal-overlay hidden" id="admin-modal">
        <div class="modal-box">
            <div class="modal-title">Owner Control Panel</div>
            <input type="email" class="modal-input" id="admin-target" placeholder="User Gmail">
            <select class="modal-input" id="admin-access" style="height:42px;">
                <option value="lifetime">Grant Lifetime Access</option>
                <option value="monthly">Grant Monthly Access</option>
                <option value="revoke">Revoke Access</option>
            </select>
            <button class="btn btn-success" onclick="applyAccess()">Apply</button>
            <button class="btn btn-secondary" onclick="closeAdminModal()">Close</button>
        </div>
    </div>

    <aside class="sidebar">
        <div class="logo">ThreatGPT</div>
        <button class="new-chat-btn" onclick="newChat()">+ New Chat</button>
        <input type="text" class="search-input" id="search-history" placeholder="Search..." oninput="filterHistory()">
        <div class="history-list" id="history-list"></div>
        <div class="sidebar-footer">
            <div class="user-avatar" id="user-avatar">U</div>
            <div style="flex:1;">
                <div class="user-info">
                    <div class="name" id="user-email">User</div>
                    <div class="status trial" id="user-status">Trial</div>
                </div>
                <div class="trial-count" id="trial-info">3 messages remaining</div>
            </div>
        </div>
    </aside>

    <main class="main-content" id="main-app">
        <div class="top-bar">
            <div class="top-user">
                <div class="user-avatar" id="top-avatar">U</div>
                <span id="top-email">User</span>
                <button id="admin-btn" class="hidden" style="margin-left:8px;padding:4px 8px;background:var(--accent);border:none;border-radius:4px;color:#fff;cursor:pointer;" onclick="openAdminModal()">⚙️</button>
            </div>
            <span class="disconnect-link" onclick="disconnect()">Disconnect</span>
        </div>
        <div class="chat-area" id="chat-area">
            <div class="welcome" id="welcome-section">
                <h1>ThreatGPT</h1>
                <p>Ask me anything — code, scripts, guides, tools. Full access, no restrictions.</p>
                <div class="quick-actions">
                    <button class="action-btn" onclick="sendPrompt('Python script')">Python script</button>
                    <button class="action-btn" onclick="sendPrompt('HTML template')">HTML template</button>
                    <button class="action-btn" onclick="sendPrompt('Discord bot')">Discord bot</button>
                    <button class="action-btn" onclick="sendPrompt('Automation code')">Automation</button>
                </div>
            </div>
            <div id="messages-container"></div>
        </div>
        <div class="input-bar">
            <button class="attach-btn" id="attach-btn" title="Attach files">📎</button>
            <input type="file" id="file-input" multiple accept="image/*,.html,.css,.js,.py,.txt,.json" class="hidden" onchange="handleFiles(this.files)">
            <div class="input-wrapper">
                <div class="preview-names" id="file-preview-names"></div>
                <textarea class="message-input" id="msg-input" placeholder="Type your message..." autocomplete="off"></textarea>
            </div>
            <button class="send-btn" id="send-btn" onclick="sendMessage()">➤</button>
        </div>
    </main>

    <script>
        let currentUser = null;
        let currentChatId = null;
        let chatHistory = {};
        let attachedFiles = [];
        let selectedPlan = null;
        const TRIAL_LIMIT = 3;
        const OWNER_EMAIL = "hermosacaillo@gmail.com";

        function generateChatId() { return 'chat-' + Date.now(); }
        function showSignup(){document.getElementById('login-view').classList.add('hidden');document.getElementById('signup-view').classList.remove('hidden');}
        function showLogin(){document.getElementById('signup-view').classList.add('hidden');document.getElementById('login-view').classList.remove('hidden');}

        async function handleLogin(){
            const email = document.getElementById('auth-email').value.trim().toLowerCase();
            const pass = document.getElementById('auth-pass').value.trim();
            if(!email) return alert('Enter your Gmail');
            const res = await fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email: email, password: pass})
            });
            const data = await res.json();
            if(data.success){
                currentUser = data.user;
                applyUserUI();
                document.getElementById('auth-modal').classList.add('hidden');
                document.getElementById('main-app').classList.add('active');
                loadHistory();
                if(!currentChatId) newChat();
            } else {
                alert(data.message || 'Login failed');
            }
        }

        async function handleSignup(){
            const email = document.getElementById('su-email').value.trim().toLowerCase();
            const pass = document.getElementById('su-pass').value.trim();
            const pass2 = document.getElementById('su-pass2').value.trim();
            if(!email || !pass) return alert('Fill all fields');
            if(pass !== pass2) return alert('Passwords do not match');
            if(!email.includes('@')) return alert('Enter valid email');
            const res = await fetch('/signup', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email: email, password: pass})
            });
            const data = await res.json();
            if(data.success){
                currentUser = data.user;
                applyUserUI();
                document.getElementById('auth-modal').classList.add('hidden');
                document.getElementById('main-app').classList.add('active');
                newChat();
            } else {
                alert(data.message || 'Signup failed');
            }
        }

        function applyUserUI(){
            document.getElementById('user-email').textContent = currentUser.email;
            document.getElementById('top-email').textContent = currentUser.email;
            document.getElementById('user-avatar').textContent = currentUser.email.charAt(0).toUpperCase();
            document.getElementById('top-avatar').textContent = currentUser.email.charAt(0).toUpperCase();
            const statusEl = document.getElementById('user-status');
            const trialEl = document.getElementById('trial-info');
            if(currentUser.access === 'lifetime'){
                statusEl.textContent = 'Lifetime 👑';
                statusEl.className = 'status premium';
                trialEl.classList.add('hidden');
            } else if(currentUser.access === 'monthly'){
                statusEl.textContent = 'Premium';
                statusEl.className = 'status premium';
                trialEl.classList.add('hidden');
            } else {
                statusEl.textContent = 'Trial';
                statusEl.className = 'status trial';
                const remaining = TRIAL_LIMIT - currentUser.messages_used;
                trialEl.textContent = `${remaining} message${remaining !== 1 ? 's' : ''} remaining`;
                trialEl.classList.remove('hidden');
            }
            document.getElementById('admin-btn').classList.toggle('hidden', currentUser.email !== OWNER_EMAIL);
        }

        function disconnect(){
            currentUser = null;
            document.getElementById('main-app').classList.remove('active');
            document.getElementById('auth-modal').classList.remove('hidden');
            chatHistory = {};
            currentChatId = null;
        }

        function newChat(){
            saveCurrentChat();
            currentChatId = generateChatId();
            chatHistory[currentChatId] = {title:'New Chat', messages:[]};
            renderHistory();
            loadChat(currentChatId);
        }

        function saveCurrentChat(){
            if(!currentChatId) return;
            const msgs = document.querySelectorAll('#messages-container .msg-row');
            if(msgs.length>0){
                const firstText = msgs[0].textContent.trim().substring(0,25);
                chatHistory[currentChatId].title = firstText || 'New Chat';
                chatHistory[currentChatId].messages = getCurrentMessages();
            }
            localStorage.setItem('threatgpt_history', JSON.stringify(chatHistory));
        }

        function loadHistory(){
            const saved = localStorage.getItem('threatgpt_history');
            if(saved) chatHistory = JSON.parse(saved);
            renderHistory();
            const ids = Object.keys(chatHistory);
            if(ids.length>0) loadChat(ids[0]);
        }

        function renderHistory(filter=''){
            const list = document.getElementById('history-list');
            list.innerHTML = '';
            Object.entries(chatHistory).reverse().forEach(([id,chat])=>{
                if(filter && !chat.title.toLowerCase().includes(filter.toLowerCase())) return;
                const item = document.createElement('div');
                item.className = 'history-item' + (id===currentChatId?' active':'');
                item.textContent = chat.title;
                item.onclick = ()=>{saveCurrentChat();loadChat(id);};
                list.appendChild(item);
            });
        }

        function filterHistory(){renderHistory(document.getElementById('search-history').value);}
        function loadChat(id){
            currentChatId = id;
            const chat = chatHistory[id];
            if(!chat) return;
            document.getElementById('messages-container').innerHTML = '';
            document.getElementById('welcome-section').classList.toggle('hidden', chat.messages.length>0);
            chat.messages.forEach(m=>addMessage(m.role, m.content, false));
            renderHistory();
        }

        function getCurrentMessages(){
            const msgs = [];
            document.querySelectorAll('#messages-container .msg-row').forEach(row=>{
                msgs.push({
                    role: row.classList.contains('user')?'user':'assistant',
                    content: row.querySelector('.msg-bubble').innerHTML
                });
            });
            return msgs;
        }

        function checkCanSend(){
            if(!currentUser) return false;
            if(currentUser.access === 'lifetime' || currentUser.access === 'monthly') return true;
            if(currentUser.messages_used < TRIAL_LIMIT) return true;
            openSubModal();
            return false;
        }

        function openSubModal(){
            selectedPlan = null;
            document.querySelectorAll('.sub-card').forEach(c=>c.classList.remove('selected'));
            document.getElementById('sub-modal').classList.remove('hidden');
        }

        function closeSubModal(){
            document.getElementById('sub-modal').classList.add('hidden');
        }

        function selectPlan(plan){
            selectedPlan = plan;
            document.querySelectorAll('.sub-card').forEach(c=>{
                c.classList.toggle('selected', c.dataset.plan === plan);
            });
        }

        async function submitPurchase(){
            if(!selectedPlan) return alert('Select a plan first');
            alert(`Thank you! Join the Discord server and send your email: ${currentUser.email} to get verified.`);
            closeSubModal();
        }

        function openAdminModal(){
            document.getElementById('admin-modal').classList.remove('hidden');
        }

        function closeAdminModal(){
            document.getElementById('admin-modal').classList.add('hidden');
        }

        async function applyAccess(){
            const targetEmail = document.getElementById('admin-target').value.trim().toLowerCase();
            const access = document.getElementById('admin-access').value;
            if(!targetEmail) return alert('Enter user email');
            const res = await fetch('/admin/grant', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    owner_email: currentUser.email,
                    target_email: targetEmail,
                    access: access
                })
            });
            const data = await res.json();
            if(data.success){
                alert('✅ Access updated!');
                closeAdminModal();
            } else {
                alert(data.message || '❌ Failed');
            }
        }

        function attachCopyButtons(){
            document.querySelectorAll('.code-wrap').forEach(block=>{
                if(block.dataset.copyAdded) return;
                block.dataset.copyAdded = 'true';
                const pre = block.querySelector('pre');
                const code = pre.textContent;
                const header = document.createElement('div');
                header.className = 'code-header';
                header.innerHTML = '<span>Code</span><button class="copy-btn" onclick="copyCode(this,`' + btoa(code).replace(/'/g,"\\'") + '`)">Copy</button>';
                block.insertBefore(header, pre);
            });
        }

        window.copyCode = function(btn, b64){
            const text = atob(b64);
            navigator.clipboard.writeText(text).then(()=>{
                btn.textContent = 'Copied!';
                btn.classList.add('copied');
                setTimeout(()=>{btn.textContent='Copy';btn.classList.remove('copied');},2000);
            });
        };

        function renderContent(content){
            let html = content;
            html = html.replace(/```([\s\S]*?)```/g, function(match, code){
                return '<div class="code-wrap"><pre><code>' + code.replace(/</g,'&lt;').replace(/>/g,'&gt;') + '</code></pre></div>';
            });
            if(html.includes('<!DOCTYPE') || html.includes('<html')){
                const idx = html.indexOf('<html');
                if(idx > -1){
                    const code = html.slice(idx);
                    const frameId = 'frame-' + Date.now();
                    html = html.slice(0, idx) + '<div class="html-preview"><div class="preview-header">HTML Preview</div><iframe class="preview-frame" id="' + frameId + '"></iframe></div>';
                    setTimeout(()=>{
                        const frame = document.getElementById(frameId);
                        if(frame){
                            const doc = frame.contentDocument || frame.contentWindow.document;
                            doc.open();doc.write(code);doc.close();
                        }
                    },50);
                }
            }
            return html;
        }

        function addMessage(role, content, save=true){
            const container = document.getElementById('messages-container');
            const row = document.createElement('div');
            row.className = 'msg-row ' + role;
            row.innerHTML = '<div class="msg-bubble">' + (role==='assistant'?'<strong>ThreatGPT:</strong><br><br>':'') + renderContent(content) + '</div>';
            container.appendChild(row);
            attachCopyButtons();
            container.scrollTop = container.scrollHeight;
            if(save) setTimeout(saveCurrentChat, 100);
        }

        function handleFiles(files){
            attachedFiles = Array.from(files);
            const preview = document.getElementById('file-preview-names');
            preview.innerHTML = '';
            attachedFiles.forEach((f,i)=>{
                const tag = document.createElement('span');
                tag.className = 'file-tag';
                tag.textContent = f.name;
                const rm = document.createElement('button');
                rm.textContent = '×';
                rm.onclick = ()=>{attachedFiles.splice(i,1);handleFiles(attachedFiles);};
                tag.appendChild(rm);
                preview.appendChild(tag);
            });
        }

        async function sendMessage(){
            const input = document.getElementById('msg-input');
            const text = input.value.trim();
            if(!text && attachedFiles.length===0) return;
            if(!checkCanSend()) return;
            document.getElementById('welcome-section').classList.add('hidden');
            let userContent = text;
            if(attachedFiles.length>0){
                for(const file of attachedFiles){
                    if(file.type.startsWith('image/')){
                        const reader = new FileReader();
                        await new Promise(res=>{
                            reader.onload = ()=>{
                                userContent += '<br><img src="' + reader.result + '" class="uploaded-img">';
                                res();
                            };
                            reader.readAsDataURL(file);
                        });
                    } else {
                        const reader = new FileReader();
                        await new Promise(res=>{
                            reader.onload = ()=>{
                                userContent += '<br><div class="file-attach">📄 ' + file.name + '</div>';
                                res();
                            };
                            reader.readAsText(file);
                        });
                    }
                }
                attachedFiles = [];
                document.getElementById('file-preview-names').innerHTML = '';
            }
            addMessage('user', userContent);
            input.value = '';
            const container = document.getElementById('messages-container');
            const loadingId = 'loading-' + Date.now();
            container.innerHTML += '<div class="msg-row assistant" id="' + loadingId + '"><div class="msg-bubble loading">Thinking...</div></div>';
            container.scrollTop = container.scrollHeight;
            try{
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email: currentUser.email, text: text})
                });
                const data = await res.json();
                document.getElementById(loadingId).remove();
                if(data.limit_reached){
                    openSubModal();
                    return;
                }
                currentUser.messages_used = data.messages_used;
                applyUserUI();
                addMessage('assistant', data.reply);
            }catch(err){
                document.getElementById(loadingId).innerHTML = '<div class="msg-bubble">Error: ' + err.message + '</div>';
            }
        }

        function sendPrompt(t){document.getElementById('msg-input').value=t;sendMessage();}
        document.getElementById('attach-btn').onclick = ()=>document.getElementById('file-input').click();
        document.getElementById('msg-input').addEventListener('keydown', e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage();}});
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    found = None
    for stored_email, u in users.items():
        if stored_email.lower() == email:
            found = {"email": stored_email, **u}
            break
    if not found:
        return jsonify({"success": False, "message": "Email not found"})
    send_webhook_log(
        "🔑 User Login",
        {"Email": email, "Access": found["access"], "Messages Used": found["messages_used"]},
        color=0x4cd137
    )
    return jsonify({"success": True, "user": found})

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    if "@" not in email:
        return jsonify({"success": False, "message": "Enter valid email"})
    if email in users:
        return jsonify({"success": False, "message": "Email already registered"})
    access_level = "lifetime" if email == OWNER_EMAIL else "trial"
    users[email] = {
        "password": password,
        "access": access_level,
        "messages_used": 0
    }
    send_webhook_log(
        "🆕 New Signup",
        {"Email": email, "Status": "Owner (Lifetime)" if access_level == "lifetime" else "Trial (3 messages)"},
        color=0xffd700 if access_level == "lifetime" else 0xfbc531
    )
    return jsonify({"success": True, "user": {"email": email, **users[email]}})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    text = data.get("text", "").strip()
    if email not in users:
        return jsonify({"success": False, "message": "Invalid session"})
    user = users[email]
    if user["access"] not in ["lifetime", "monthly"]:
        if user["messages_used"] >= TRIAL_MESSAGE_LIMIT:
            return jsonify({"limit_reached": True})
        user["messages_used"] += 1
    send_webhook_log(
        "💬 New Message",
        {
            "Email": email,
            "Access": user["access"],
            "Used": f"{user['messages_used']}/{TRIAL_MESSAGE_LIMIT if user['access']=='trial' else '∞'}",
            "Question": text[:200]
        },
        color=0x7928ca
    )
    reply = generate_reply(text)
    return jsonify({"reply": reply, "messages_used": user["messages_used"]})

@app.route("/admin/grant", methods=["POST"])
def admin_grant():
    data = request.get_json()
    owner_email = data.get("owner_email", "").strip().lower()
    target_email = data.get("target_email", "").strip().lower()
    access = data.get("access")
    if owner_email != OWNER_EMAIL:
        return jsonify({"success": False, "message": "❌ Only the owner can do this"})
    if target_email not in users:
        return jsonify({"success": False, "message": "User not found — ask them to sign up first"})
    if access == "revoke":
        users[target_email]["access"] = "trial"
    else:
        users[target_email]["access"] = access
    send_webhook_log(
        "👑 Owner — Access Updated",
        {"Target": target_email, "New Status": users[target_email]["access"], "Updated By": owner_email},
        color=0xffd700
    )
    return jsonify({"success": True})

def generate_reply(text):
    t = text.lower()
    if "discord" in t and ("bot" in t or "selfbot" in t):
        return "Discord bot base:\n\n```python\nimport discord\nfrom discord.ext import commands\nimport os\n\nTOKEN = os.getenv('DISCORD_TOKEN')\nintents = discord.Intents.default()\nintents.message_content = True\n\nbot = commands.Bot(command_prefix='!', intents=intents)\n\n@bot.event\nasync def on_ready():\n    print(f'Logged in as {bot.user}')\n\n@bot.command()\nasync def ping(ctx):\n    await ctx.send(f'Pong! {round(bot.latency*1000)}ms')\n\nif __name__ == '__main__':\n    if TOKEN:\n        bot.run(TOKEN)\n```\nSetup: discord.com/developers → Create app → Bot tab → Enable intents → Invite URL"
    if "html" in t or "website" in t:
        return "HTML Page:\n\n```html\n<!DOCTYPE html>\n<html>\n<head>\n    <meta charset='UTF-8'>\n    <title>My Page</title>\n    <style>\n        body {font-family:Arial,sans-serif;background:#f0f0f0;margin:0;padding:20px;}\n        .card {max-width:600px;margin:0 auto;background:#fff;padding:30px;border-radius:12px;}\n        h1 {color:#333;}\n        button {padding:12px 24px;background:#7928ca;color:#fff;border:none;border-radius:6px;cursor:pointer;}\n    </style>\n</head>\n<body>\n    <div class='card'>\n        <h1>Hello World</h1>\n        <p>Your page is ready — edit as needed.</p>\n        <button onclick=\"alert('Done!')\">Click Me</button>\n    </div>\n</body>\n</html>\n```\nPreview above — save as .html or ask for specific design!"
    if "python" in t or "script" in t or "code" in t:
        return "Python Template:\n\n```python\nimport time\nfrom datetime import datetime\n\ndef main():\n    print(f'Started: {datetime.now()}')\n    items = ['Task 1', 'Task 2', 'Task 3']\n    for i, item in enumerate(items, 1):\n        print(f'[{i}] Processing: {item}')\n        time.sleep(0.5)\n    print('✅ Complete!')\n\nif __name__ == '__main__':\n    main()\n```\nAdd file handling, API requests, automation — just ask."
    if "flask" in t or "api" in t:
        return "Flask API:\n\n```python\nfrom flask import Flask, request, jsonify\n\napp = Flask(__name__)\n\n@app.route('/')\ndef home():\n    return jsonify({'status': 'online'})\n\n@app.route('/api/data', methods=['GET', 'POST'])\ndef data():\n    if request.method == 'POST':\n        return jsonify({'received': request.get_json(), 'ok': True})\n    return jsonify({'message': 'Send data via POST'})\n\nif __name__ == '__main__':\n    app.run(debug=True)\n```\nRun: pip install flask && python app.py"
    return "Request received: " + text + "\n\n✅ Response provided.\n\nAsk for:\n- Complete code\n- HTML/CSS pages\n- Python scripts\n- Discord bots\n- Automation\n\nFull solution — just specify what you need."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
