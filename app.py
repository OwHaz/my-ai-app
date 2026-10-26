import os
from flask import Flask, request, render_template_string, jsonify
import requests
import random
from datetime import datetime

app = Flask(__name__)

# ==============================================
# SA RENDER MO ILALAGAY ANG MGA KEY — HINDI DITO
# ==============================================
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "").strip()
SELECTED_MODEL = "meta-llama/llama-3-8b-instruct"
OWNER_EMAIL = "blahlhamara@gmail.com"
TRIAL_MESSAGE_LIMIT = 3
APP_NAME = "ThreatGPT"

# ✅ TAMA ANG URL — WALANG DAGDAG NA / SA DULO
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
        <input type="text" class="search-input" id="search-history" placeholder="
