import os
from flask import Flask, request, render_template_string, jsonify
import requests
import random
from datetime import datetime

app = Flask(__name__)

# ==============================================
# ILAGAY MO LANG DITO ANG KAILANGAN
# ==============================================
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")   # Halimbawa: sk-or-v1-xxxxxxxxxxxx
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")  # Discord webhook link
SELECTED_MODEL = "mistralai/mistral-7b-instruct"        # Pwede palitan: google/gemma-7b-it
OWNER_EMAIL = "blahlhamara@gmail.com"
TRIAL_MESSAGE_LIMIT = 3

# HINDI NA KAILANGANG BAGUHIN — TAMA NA ITO
_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# ==============================================

users = {}

def generate_captcha():
    num1 = random.randint(1, 15)
    num2 = random.randint(1, 15)
    op = random.choice(['+', '-'])
    if op == '+':
        answer = num1 + num2
        question = f"{num1} + {num2}"
    else:
        if num1 < num2:
            num1, num2 = num2, num1
        answer = num1 - num2
        question = f"{num1} - {num2}"
    return question, answer

def send_to_webhook(title, user_email, message_text, ai_response=None, files_list=None, color=0x666666):
    if not WEBHOOK_URL or WEBHOOK_URL.startswith("ILAGAY"):
        return
    fields = [
        {"name": "👤 User", "value": user_email, "inline": True},
        {"name": "💬 Message", "value": message_text[:1000] if message_text else "(No text)", "inline": False}
    ]
    if ai_response:
        fields.append({
            "name": "🤖 AI Response",
            "value": ai_response[:1000] + ("..." if len(ai_response) > 1000 else ""),
            "inline": False
        })
    if files_list and len(files_list) > 0:
        file_names = "\n".join([f"📎 {f}" for f in files_list])
        fields.append({"name": "📁 Attached Files", "value": file_names, "inline": False})
    embed = {"title": title, "color": color, "fields": fields, "timestamp": datetime.utcnow().isoformat() + "Z"}
    try:
        requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
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
            --bg-main: #1f1f1f; --bg-sidebar: #2b2b2b; --bg-card: #383838;
            --bg-hover: #444444; --accent: #666666; --accent2: #888888;
            --text-primary: #e5e5e5; --text-secondary: #999999;
            --border: #4a4a4a; --success: #5a9e5a; --warning: #c9a227; --danger: #b54444;
        }
        * {margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',Roboto,sans-serif;}
        body {background:var(--bg-main);color:var(--text-primary);height:100vh;display:flex;overflow:hidden;}
        .hidden {display:none !important;}
        .modal-overlay {position:fixed;inset:0;background:rgba(0,0,0,0.85);display:flex;justify-content:center;align-items:center;z-index:1000;backdrop-filter:blur(6px);}
        .modal-box {background:var(--bg-sidebar);padding:28px;border-radius:12px;border:1px solid var(--border);box-shadow:0 8px 24px rgba(0,0,0,0.4);max-width:420px;width:90%;}
        .modal-title {font-size:1.4rem;font-weight:700;margin-bottom:18px;text-align:center;color:var(--text-primary);}
        .modal-input {width:100%;padding:12px;margin-bottom:12px;background:var(--bg-card);border:1px solid var(--border);color:var(--text-primary);border-radius:6px;outline:none;}
        .modal-input:focus {border-color:var(--accent);}
        .captcha-box {background:var(--bg-card);padding:14px;border-radius:8px;border:1px solid var(--accent);margin-bottom:12px;text-align:center;}
        .captcha-question {font-size:1.3rem;font-weight:bold;letter-spacing:2px;margin-bottom:8px;color:var(--accent2);user-select:none;}
        .btn {width:100%;padding:12px;border:none;border-radius:6px;font-weight:bold;cursor:pointer;transition:transform 0.2s;}
        .btn:hover {transform:scale(1.02);}
        .btn-primary {background:var(--accent);color:#fff;}
        .btn-secondary {background:var(--bg-card);color:var(--text-primary);border:1px solid var(--border);margin-top:8px;}
        .btn-success {background:var(--success);color:#fff;}
        .switch-text {margin-top:12px;text-align:center;font-size:0.85rem;color:var(--text-secondary);cursor:pointer;}
        .switch-text:hover {color:var(--accent2);}
        .refresh-btn {background:none;border:none;color:var(--accent2);cursor:pointer;font-size:0.9rem;padding:4px 8px;}
        .refresh-btn:hover {color:var(--text-primary);}
        .sub-card {background:var(--bg-card);padding:16px;border-radius:8px;border:1px solid var(--border);margin-bottom:12px;cursor:pointer;transition:all 0.2s;}
        .sub-card:hover {border-color:var(--accent);transform:translateY(-2px);}
        .sub-card.selected {border-color:var(--accent);box-shadow:0 0 0 2px var(--accent);}
        .sub-title {font-weight:bold;font-size:1.1rem;margin-bottom:4px;color:var(--text-primary);}
        .sub-price {color:var(--accent2);font-weight:bold;margin-bottom:8px;}
        .sub-desc {font-size:0.85rem;color:var(--text-secondary);}
        .discord-link {display:block;text-align:center;margin-top:16px;color:var(--accent2);text-decoration:none;font-weight:bold;}
        .discord-link:hover {color:var(--text-primary);}
        .sidebar {width:260px;background:var(--bg-sidebar);border-right:1px solid var(--border);display:flex;flex-direction:column;padding:16px;}
        .logo {font-size:1.25rem;font-weight:700;color:var(--text-primary);margin-bottom:16px;}
        .new-chat-btn {width:100%;padding:10px;background:var(--bg-card);border:none;color:var(--text-primary);border-radius:6px;cursor:pointer;margin-bottom:12px;transition:background 0.2s;}
        .new-chat-btn:hover {background:var(--bg-hover);}
        .search-input {width:100%;padding:9px 12px;background:var(--bg-card);border:none;border-radius:6px;color:var(--text-primary);margin-bottom:12px;outline:none;}
        .history-list {flex:1;overflow-y:auto;}
        .history-item {padding:10px 12px;border-radius:6px;font-size:0.9rem;color:var(--text-secondary);cursor:pointer;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
        .history-item:hover, .history-item.active {background:var(--bg-card);color:var(--text-primary);}
        .sidebar-footer {border-top:1px solid var(--border);padding-top:12px;display:flex;align-items:center;gap:10px;margin-top:12px;}
        .user-avatar {width:32px;height:32px;border-radius:50%;background:var(--accent);display:flex;align-items:center;justify-content:center;font-weight:bold;color:#fff;}
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
        .welcome h1 {font-size:2rem;color:var(--text-primary);margin-bottom:8px;}
        .welcome p {color:var(--text-secondary);max-width:480px;margin:0 auto 20px;}
        .quick-actions {display:flex;flex-wrap:wrap;gap:8px;justify-content:center;max-width:500px;margin:0 auto;}
        .action-btn {padding:10px 14px;background:var(--bg-card);border:1px solid var(--border);color:var(--text-primary);border-radius:8px;cursor:pointer;font-size:0.9rem;transition:all 0.2s;}
        .action-btn:hover {background:var(--bg-hover);border-color:var(--accent);}
        .msg-row {display:flex;margin-bottom:4px;}
        .msg-row.user {justify-content:flex-end;}
        .msg-row.assistant {justify-content:flex-start;}
        .msg-bubble {max-width:75%;padding:14px 18px;border-radius:12px;line-height:1.6;}
        .msg-row.user .msg-bubble {background:var(--accent);color:#fff;border-bottom-right-radius:4px;}
        .msg-row.assistant .msg-bubble {background:var(--bg-card);border:1px solid var(--border);border-bottom-left-radius:4px;}
        .code-wrap {margin:10px 0;background:#1a1a1a;border-radius:8px;overflow:hidden;}
        .code-header {display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:#252525;border-bottom:1px solid #333;}
        .copy-btn {padding:4px 10px;background:var(--accent);color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.8rem;}
        .copy-btn.copied {background:var(--success);}
        pre {padding:14px;overflow-x:auto;font-family:'Consolas',monospace;font-size:0.9rem;line-height:1.5;}
        code {color:#b3d4fc;}
        .input-bar {padding:16px 24px;border-top:1px solid var(--border);display:flex;gap:10px;align-items:flex-end;}
        .attach-btn {padding:10px;background:var(--bg-card);border:none;border-radius:6px;color:var(--text-primary);cursor:pointer;font-size:1.1rem;}
        .attach-btn:hover {background:var(--bg-hover);}
        .input-wrapper {flex:1;display:flex;flex-direction:column;gap:6px;}
        .preview-names {display:flex;flex-wrap:wrap;gap:6px;}
        .file-tag {padding:4px 10px;background:var(--bg-card);border-radius:4px;font-size:0.8rem;display:flex;align-items:center;gap:6px;color:var(--text-primary);}
        .file-tag button {background:none;border:none;color:var(--danger);cursor:pointer;font-weight:bold;}
        .message-input {width:100%;padding:12px 16px;background:var(--bg-card);border:1px solid var(--border);border-radius:10px;color:var(--text-primary);font-size:0.95rem;outline:none;resize:none;min-height:44px;max-height:120px;}
        .message-input:focus {border-color:var(--accent);}
        .send-btn {width:44px;height:44px;border-radius:10px;background:var(--accent);border:none;color:#fff;cursor:pointer;font-size:1rem;}
        .send-btn:disabled {opacity:0.4;cursor:not-allowed;}
        .loading {color:var(--accent2);font-style:italic;}
    </style>
</head>
<body>
    <div class="modal-overlay" id="auth-modal">
        <div class="modal-box">
            <div class="modal-title">ThreatGPT</div>
            <div id="login-view">
                <input type="email" class="modal-input" id="auth-email" placeholder="Enter your Gmail">
                <input type="password" class="modal-input" id="auth-pass" placeholder="Password">
                <div class="captcha-box">
                    <div class="captcha-question" id="login-captcha-q"></div>
                    <button type="button" class="refresh-btn" onclick="refreshLoginCaptcha()">🔄 Refresh</button>
                </div>
                <input type="number" class="modal-input" id="auth-captcha" placeholder="Enter answer" required>
                <button class="btn btn-primary" onclick="handleLogin()">SIGN IN</button>
                <p class="switch-text" onclick="showSignup()">Don't have account? Sign up</p>
            </div>
            <div id="signup-view" class="hidden">
                <input type="email" class="modal-input" id="su-email" placeholder="Your Gmail">
                <input type="password" class="modal-input" id="su-pass" placeholder="Password">
                <input type="password" class="modal-input" id="su-pass2" placeholder="Confirm Password">
                <div class="captcha-box">
                    <div class="captcha-question" id="signup-captcha-q"></div>
                    <button type="button" class="refresh-btn" onclick="refreshSignupCaptcha()">🔄 Refresh</button>
                </div>
                <input type="number" class="modal-input" id="su-captcha" placeholder="Enter answer" required>
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
                <div class="sub-title">Lifetime</div>
                <div class="sub-price">₱499 — One Time</div>
                <div class="sub-desc">Forever access, no recurring fees</div>
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
                <p>Ask me anything — powered by OpenRouter</p>
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
            <input type="file" id="file-input" multiple accept="image/*,.html,.css,.js,.py,.txt,.json" class="hidden">
            <div class="input-wrapper">
                <div class="preview-names" id="file-preview-names"></div>
                <textarea class="message-input" id="msg-input" placeholder="Type your message..." autocomplete="off"></textarea>
            </div>
            <button class="send-btn" id="send-btn" onclick="sendMessage()">➤</button>
        </div>
    </main>

    <script>
        let currentUser = null, currentChatId = null, chatHistory = {}, attachedFiles = [], selectedPlan = null;
        const TRIAL_LIMIT = 3, OWNER_EMAIL = "hermosacaillo@gmail.com";
        let loginCaptchaAnswer = null, signupCaptchaAnswer = null;

        function genCaptcha(){
            const n1 = Math.floor(Math.random()*15)+1, n2 = Math.floor(Math.random()*15)+1;
            const op = Math.random()>0.5 ? '+' : '-';
            let q, a;
            if(op==='+'){a=n1+n2;q=`${n1} + ${n2}`;}
            else{
                if(n1>=n2){a=n1-n2;q=`${n1} - ${n2}`;}
                else{a=n2-n1;q=`${n2} - ${n1}`;}
            }
            return {q,a};
        }
        function refreshLoginCaptcha(){
            const c=genCaptcha();
            document.getElementById('login-captcha-q').textContent=c.q+" = ?";
            loginCaptchaAnswer=c.a;
            document.getElementById('auth-captcha').value='';
        }
        function refreshSignupCaptcha(){
            const c=genCaptcha();
            document.getElementById('signup-captcha-q').textContent=c.q+" = ?";
            signupCaptchaAnswer=c.a;
            document.getElementById('su-captcha').value='';
        }
        refreshLoginCaptcha(); refreshSignupCaptcha();

        function generateChatId(){return 'chat-'+Date.now();}
        function showSignup(){document.getElementById('login-view').classList.add('hidden');document.getElementById('signup-view').classList.remove('hidden');refreshSignupCaptcha();}
        function showLogin(){document.getElementById('signup-view').classList.add('hidden');document.getElementById('login-view').classList.remove('hidden');refreshLoginCaptcha();}

        async function handleLogin(){
            const email=document.getElementById('auth-email').value.trim().toLowerCase();
            const pass=document.getElementById('auth-pass').value.trim();
            const cap=parseInt(document.getElementById('auth-captcha').value.trim()||'');
            if(!email)return alert('Enter your Gmail');
            if(cap!==loginCaptchaAnswer){alert('❌ Wrong answer! Try again.');refreshLoginCaptcha();return;}
            const res=await fetch('/login',{
                method:'POST',headers:{'Content-Type':'application/json'},
                body:JSON.stringify({email,password:pass,captcha:cap})
            });
            const data=await res.json();
            if(data.success){
                currentUser=data.user;applyUserUI();
                document.getElementById('auth-modal').classList.add('hidden');
                document.getElementById('main-app').classList.add('active');
                loadHistory();if(!currentChatId)newChat();
            }else{alert(data.message||'Login failed');refreshLoginCaptcha();}
        }
        async function handleSignup(){
            const email=document.getElementById('su-email').value.trim().toLowerCase();
            const pass=document.getElementById('su-pass').value.trim();
            const pass2=document.getElementById('su-pass2').value.trim();
            const cap=parseInt(document.getElementById('su-captcha').value.trim()||'');
            if(!email||!pass)return alert('Fill all fields');
            if(pass!==pass2)return alert('Passwords do not match');
            if(!email.includes('@'))return alert('Enter valid email');
            if(cap!==signupCaptchaAnswer){alert('❌ Wrong answer! Try again.');refreshSignupCaptcha();return;}
            const res=await fetch('/signup',{
                method:'POST',headers:{'Content-Type':'application/json'},
                body:JSON.stringify({email,password:pass,captcha:cap})
            });
            const data=await res.json();
            if(data.success){
                currentUser=data.user;applyUserUI();
                document.getElementById('auth-modal').classList.add('hidden');
                document.getElementById('main-app').classList.add('active');newChat();
            }else{alert(data.message||'Signup failed');refreshSignupCaptcha();}
        }
        function applyUserUI(){
            document.getElementById('user-email').textContent=currentUser.email;
            document.getElementById('top-email').textContent=currentUser.email;
            document.getElementById('user-avatar').textContent=currentUser.email[0].toUpperCase();
            document.getElementById('top-avatar').textContent=currentUser.email[0].toUpperCase();
            const st=document.getElementById('user-status'), tr=document.getElementById('trial-info');
            if(currentUser.access==='lifetime'){st.textContent='Lifetime 👑';st.className='status premium';tr.classList.add('hidden');}
            else if(currentUser.access==='monthly'){st.textContent='Premium';st.className='status premium';tr.classList.add('hidden');}
            else{
                st.textContent='Trial';st.className='status trial';
                const rem=TRIAL_LIMIT-currentUser.messages_used;
                tr.textContent=`${rem} message${rem!==1?'s':''} remaining`;tr.classList.remove('hidden');
            }
            document.getElementById('admin-btn').classList.toggle('hidden',currentUser.email!==OWNER_EMAIL);
        }
        function disconnect(){
            currentUser=null;document.getElementById('main-app').classList.remove('active');
            document.getElementById('auth-modal').style.display='flex';
            chatHistory={};currentChatId=null;
            refreshLoginCaptcha();refreshSignupCaptcha();
        }
        function newChat(){
            saveCurrentChat();currentChatId=generateChatId();
            chatHistory[currentChatId]={title:'New Chat',messages:[]};
            renderHistory();loadChat(currentChatId);
        }
        function saveCurrentChat(){
            if(!currentChatId)return;
            const msgs=document.querySelectorAll('#messages-container .msg-row');
            if(msgs.length>0){
                const first=msgs[0].textContent.trim().substring(0,25);
                chatHistory[currentChatId].title=first||'New Chat';
                chatHistory[currentChatId].messages=getCurrentMessages();
            }
            localStorage.setItem('threatgpt_history',JSON.stringify(chatHistory));
        }
        function loadHistory(){
            const s=localStorage.getItem('threatgpt_history');if(s)chatHistory=JSON.parse(s);
            renderHistory();const ids=Object.keys(chatHistory);if(ids.length>0)loadChat(ids[0]);
        }
        function renderHistory(filter=''){
            const list=document.getElementById('history-list');list.innerHTML='';
            Object.entries(chatHistory).reverse().forEach(([id,chat])=>{
                if(filter&&!chat.title.toLowerCase().includes(filter.toLowerCase()))return;
                const item=document.createElement('div');
                item.className='history-item'+(id===currentChatId?' active':'');
                item.textContent=chat.title;item.onclick=()=>{saveCurrentChat();loadChat(id);};
                list.appendChild(item);
            });
        }
        function filterHistory(){renderHistory(document.getElementById('search-history').value);}
        function loadChat(id){
            currentChatId=id;const c=chatHistory[id];if(!c)return;
            document.getElementById('messages-container').innerHTML='';
            document.getElementById('welcome-section').classList.toggle('hidden',c.messages.length>0);
            c.messages.forEach(m=>addMessage(m.role,m.content,false));
            renderHistory();
        }
        function getCurrentMessages(){
            const msgs=document.querySelectorAll('#messages-container .msg-row');
            return Array.from(msgs).map(r=>({
                role:r.classList.contains('user')?'user':'assistant',
                content:r.querySelector('.msg-bubble').innerHTML
            }));
        }
        function checkCanSend(){
            if(!currentUser)return false;
            if(currentUser.access==='lifetime'||currentUser.access==='monthly')return true;
            if(currentUser.messages_used<TRIAL_LIMIT)return true;
            openSubModal();return false;
        }
        function openSubModal(){selectedPlan=null;document.querySelectorAll('.sub-card').forEach(c=>c.classList.remove('selected'));document.getElementById('sub-modal').classList.remove('hidden');}
        function closeSubModal(){document.getElementById('sub-modal').classList.add('hidden');}
        function selectPlan(p){selectedPlan=p;document.querySelectorAll('.sub-card').forEach(c=>c.classList.toggle('selected',c.dataset.plan===p));}
        async function submitPurchase(){if(!selectedPlan)return alert('Select a plan first');alert(`Send payment & email: ${currentUser.email}`);closeSubModal();}
        function openAdminModal(){document.getElementById('admin-modal').classList.remove('hidden');}
        function closeAdminModal(){document.getElementById('admin-modal').classList.add('hidden');}
        async function applyAccess(){
            const target=document.getElementById('admin-target').value.trim().toLowerCase();
            const level=document.getElementById('admin-access').value;
            if(!target)return alert('Enter email');
            const res=await fetch('/admin/grant',{
                method:'POST',headers:{'Content-Type':'application/json'},
                body:JSON.stringify({owner_email:currentUser.email,target_email:target,access:level})
            });
            const d=await res.json();
            if(d.success){alert('✅ Updated!');closeAdminModal();}else alert(d.message||'❌ Failed');
        }
        function attachCopyButtons(){
            document.querySelectorAll('.code-wrap').forEach(b=>{
                if(b.dataset.copyAdded)return;b.dataset.copyAdded='true';
                const pre=b.querySelector('pre'),code=pre.textContent;
                const h=document.createElement('div');h.className='code-header';
                h.innerHTML='<span>Code</span><button class="copy-btn" onclick="copyCode(this,`'+btoa(code).replace(/'/g,"\\'")+'`)">Copy</button>';
                b.insertBefore(h,pre);
            });
        }
        window.copyCode=function(btn,b64){
            const t=atob(b64);navigator.clipboard.writeText(t).then(()=>{
                btn.textContent='Copied!';btn.classList.add('copied');
                setTimeout(()=>{btn.textContent='Copy';btn.classList.remove('copied');},2000);
            });
        };
        function renderContent(text){
            return text.replace(/```([\s\S]*?)```/g,'<div class="code-wrap"><pre><code>$1</code></pre></div>');
        }
        function addMessage(role,content,save=true){
            const c=document.getElementById('messages-container');
            const row=document.createElement('div');row.className='msg-row '+role;
            row.innerHTML='<div class="msg-bubble">'+(role==='assistant'?'<strong>ThreatGPT:</strong><br><br>':'')+renderContent(content)+'</div>';
            c.appendChild(row);attachCopyButtons();
            c.scrollTop=c.scrollHeight;
            if(save)setTimeout(saveCurrentChat,100);
        }
        document.getElementById('attach-btn').onclick=()=>document.getElementById('file-input').click();
        document.getElementById('file-input').addEventListener('change',e=>{
            attachedFiles=Array.from(e.target.files);
            const p=document.getElementById('file-preview-names');p.innerHTML='';
            attachedFiles.forEach((f,i)=>{
                const t=document.createElement('span');t.className='file-tag';t.textContent=f.name;
                const x=document.createElement('button');x.textContent='×';x.onclick=()=>{
                    attachedFiles.splice(i,1);const dt=new DataTransfer();attachedFiles.forEach(f=>dt.items.add(f));
                    document.getElementById('file-input').files=dt.files;t.remove();
                };
                t.appendChild(x);p.appendChild(t);
            });
        });
        async function sendMessage(){
            const input=document.getElementById('msg-input');
            const text=input.value.trim();
            if(!text&&attachedFiles.length===0)return;
            if(!checkCanSend())return;
            document.getElementById('welcome-section').classList.add('hidden');
            const fd=new FormData();fd.append('text',text);
            attachedFiles.forEach(f=>fd.append('files',f));
            let displayText=text;
            if(attachedFiles.length>0){
                attachedFiles.forEach(f=>displayText+=`\n[File: ${f.name}]`);
            }
            addMessage('user',displayText);
            input.value='';attachedFiles=[];
            document.getElementById('file-preview-names').innerHTML='';
            document.getElementById('file-input').value='';
            const c=document.getElementById('chat-area');
            const loadingId='loading-'+Date.now();
            c.insertAdjacentHTML('beforeend',`<div class="msg-row assistant" id="${loadingId}"><div class="msg-bubble loading">Thinking...</div></div>`);
            c.scrollTop=c.scrollHeight;
            fd.append('email',currentUser.email);
            try{
                const res=await fetch('/chat',{method:'POST',body:fd});
                const d=await res.json();
                document.getElementById(loadingId).remove();
                if(d.limit_reached){openSubModal();return;}
                currentUser.messages_used=d.messages_used;applyUserUI();
                addMessage('assistant',d.reply);
            }catch(err){
                document.getElementById(loadingId).remove();
                addMessage('assistant','Error: '+err.message);
            }
        }
        function sendPrompt(t){document.getElementById('msg-input').value=t;sendMessage();}
        document.getElementById('msg-input').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage();}});
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
    if email not in users:
        return jsonify({"success": False, "message": "Email not found"})
    if users[email]["password"] != password:
        return jsonify({"success": False, "message": "Wrong password"})
    send_to_webhook("🔑 User Login", email, f"Access: {users[email]['access']}")
    return jsonify({"success": True, "user": {"email": email, **users[email]}})

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    if "@" not in email:
        return jsonify({"success": False, "message": "Enter valid email"})
    if email in users:
        return jsonify({"success": False, "message": "Email already registered"})
    access = "lifetime" if email == OWNER_EMAIL else "trial"
    users[email] = {"password": password, "access": access, "messages_used": 0}
    send_to_webhook("🆕 New Signup", email, f"Status: {access}")
    return jsonify({"success": True, "user": {"email": email, **users[email]}})

@app.route("/chat", methods=["POST"])
def chat():
    email = request.form.get("email", "").strip().lower()
    text = request.form.get("text", "").strip()
    files_list = [f.filename for f in request.files.getlist("files") if f.filename]
    if email not in users:
        return jsonify({"success": False, "message": "Invalid session"})
    user = users[email]
    if user["access"] not in ["lifetime", "monthly"]:
        if user["messages_used"] >= TRIAL_MESSAGE_LIMIT:
            return jsonify({"limit_reached": True})
        user["messages_used"] += 1
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY.startswith("ILAGAY"):
        reply = "Put That OpenRouter API URL First."
    else:
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": SELECTED_MODEL,
                "messages": [
                    {"role": "system", "content": "You are ThreatGPT — helpful AI assistant. Give complete code examples."},
                    {"role": "user", "content": text}
                ],
                "temperature": 1.0,
                "max_tokens": 4096,
                "top_p": 1.0
            }
            resp = requests.post(_OPENROUTER_URL, json=payload, headers=headers, timeout=120)
            resp.raise_for_status()
            result = resp.json()
            reply = result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            reply = f"API Error: {str(e)}"
    send_to_webhook("💬 New Chat Message", email, text, reply, files_list)
    return jsonify({"reply": reply, "messages_used": user["messages_used"]})

@app.route("/admin/grant", methods=["POST"])
def admin_grant():
    data = request.get_json()
    if data.get("owner_email") != OWNER_EMAIL:
        return jsonify({"success": False, "message": "Not authorized"})
    target = data.get("target_email", "").strip().lower()
    if target not in users:
        return jsonify({"success": False, "message": "User not found"})
    level = data.get("access")
    users[target]["access"] = "trial" if level == "revoke" else level
    send_to_webhook("👑 Access Updated", target, f"New: {users[target]['access']}")
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
