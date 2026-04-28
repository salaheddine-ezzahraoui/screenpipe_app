import os
import glob
import subprocess
import requests
import json
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, send_file

app = Flask(__name__)

OUTPUT_DIR = os.path.expanduser("~/Videos/screenpipe")
SCRIPT = os.path.expanduser("~/screenpipe_ctl.sh")
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3:latest"

CONFIG = {"quality": "1080p", "fps": 30, "audio": True, "ai_enabled": True, "auto_delete_days": 30}

def load_config():
    try:
        with open(os.path.expanduser("~/.screenpipe_config.json")) as f:
            CONFIG.update(json.load(f))
    except: pass

def save_config():
    with open(os.path.expanduser("~/.screenpipe_config.json"), "w") as f:
        json.dump(CONFIG, f)

FOUNDER = "You are Screenpipe AI assistant by Salaheddine Ezzahraoui."

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Screenpipe - Modern Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #f97316; --primary-light: #fb923c; --primary-dark: #ea580c;
            --bg: #f8f9fb; --surface: #ffffff; --surface-hover: #f1f3f5;
            --border: #e2e8f0; --text: #1e293b; --text2: #64748b;
            --success: #10b981; --danger: #ef4444;
            --shadow: 0 4px 6px -1px rgba(0,0,0,0.1); --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }
        
        .navbar { background: var(--surface); border-bottom: 1px solid var(--border); padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }
        .nav-left { display: flex; align-items: center; gap: 32px; }
        .logo { display: flex; align-items: center; gap: 10px; font-size: 18px; font-weight: 700; }
        .logo-icon { width: 36px; height: 36px; background: linear-gradient(135deg, var(--primary), var(--primary-light)); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; }
        .nav-menu { display: flex; gap: 4px; }
        .nav-item { padding: 10px 16px; color: var(--text2); font-size: 14px; font-weight: 500; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
        .nav-item:hover { background: var(--surface-hover); color: var(--text); }
        .nav-item.active { background: var(--primary); color: white; }
        .user-avatar { width: 36px; height: 36px; background: linear-gradient(135deg, #6366f1, #8b5cf6); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-size: 14px; font-weight: 600; }
        
        .main { max-width: 1200px; margin: 0 auto; padding: 24px; }
        .page { display: none; }
        .page.active { display: block; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        .page-header { margin-bottom: 24px; }
        .page-header h1 { font-size: 24px; font-weight: 700; margin-bottom: 4px; }
        .page-header p { color: var(--text2); font-size: 14px; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
        .stat-card { background: var(--surface); border-radius: 16px; padding: 20px; border: 1px solid var(--border); transition: all 0.2s; }
        .stat-card:hover { transform: translateY(-2px); box-shadow: var(--shadow); }
        .stat-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px; font-size: 22px; }
        .stat-value { font-size: 28px; font-weight: 700; }
        .stat-label { color: var(--text2); font-size: 13px; margin-top: 4px; }
        
        .two-col { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        .card { background: var(--surface); border-radius: 16px; border: 1px solid var(--border); overflow: hidden; }
        .card-header { padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
        .card-title { font-size: 15px; font-weight: 600; }
        .card-body { padding: 20px; }
        
        .record-btn { width: 100%; padding: 16px; background: var(--primary); color: white; border: none; border-radius: 12px; font-size: 15px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .record-btn:hover { background: var(--primary-dark); transform: translateY(-1px); }
        .record-btn.recording { background: var(--danger); }
        
        .status-badge { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: var(--bg); border-radius: 8px; font-size: 13px; }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--text2); }
        .status-dot.active { background: var(--danger); animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        
        .rec-list { display: flex; flex-direction: column; gap: 10px; }
        .rec-item { display: flex; align-items: center; gap: 12px; padding: 12px; background: var(--bg); border-radius: 12px; transition: all 0.2s; }
        .rec-item:hover { background: var(--surface-hover); }
        .rec-thumb { width: 56px; height: 36px; background: linear-gradient(135deg, var(--primary), var(--primary-light)); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; cursor: pointer; font-size: 14px; }
        .rec-info { flex: 1; }
        .rec-name { font-size: 13px; font-weight: 500; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 200px; }
        .rec-meta { font-size: 12px; color: var(--text2); }
        .rec-actions { display: flex; gap: 6px; }
        .rec-btn { width: 32px; height: 32px; border: none; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 12px; }
        .rec-btn.play { background: var(--primary); color: white; }
        .rec-btn.dl { background: var(--success); color: white; }
        .rec-btn.del { background: var(--danger); color: white; }
        
        .empty { text-align: center; padding: 40px; color: var(--text2); }
        
        .chat-messages { height: 280px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .chat-msg { max-width: 80%; padding: 12px 16px; border-radius: 16px; font-size: 13px; line-height: 1.5; }
        .chat-msg.user { align-self: flex-end; background: var(--primary); color: white; border-bottom-right-radius: 4px; }
        .chat-msg.ai { align-self: flex-start; background: var(--bg); border-bottom-left-radius: 4px; }
        .chat-input { display: flex; gap: 10px; margin-top: 12px; }
        .chat-input input { flex: 1; padding: 12px 16px; border: 1px solid var(--border); border-radius: 12px; font-size: 13px; font-family: inherit; }
        .chat-input input:focus { outline: none; border-color: var(--primary); }
        .chat-input button { padding: 12px 20px; background: var(--primary); color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: 500; }
        
        .settings-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .form-group { margin-bottom: 16px; }
        .form-label { display: block; font-size: 13px; font-weight: 500; margin-bottom: 8px; }
        .form-select { width: 100%; padding: 12px 14px; border: 1px solid var(--border); border-radius: 10px; font-size: 13px; background: var(--surface); }
        .form-check { display: flex; align-items: center; gap: 10px; padding: 12px; background: var(--bg); border-radius: 10px; font-size: 13px; cursor: pointer; }
        .form-check input { width: 18px; height: 18px; }
        
        .docs-layout { display: grid; grid-template-columns: 240px 1fr; gap: 0; background: var(--surface); border-radius: 16px; border: 1px solid var(--border); overflow: hidden; }
        .docs-sidebar { background: var(--bg); padding: 16px 0; }
        .docs-link { padding: 12px 20px; color: var(--text2); font-size: 14px; font-weight: 500; cursor: pointer; border-left: 3px solid transparent; }
        .docs-link:hover { color: var(--text); background: var(--surface); }
        .docs-link.active { color: var(--primary); background: var(--surface); border-left-color: var(--primary); }
        .docs-content { padding: 32px; }
        .docs-section { display: none; }
        .docs-section.active { display: block; }
        .docs-section h2 { font-size: 22px; font-weight: 700; margin-bottom: 12px; }
        .docs-section p { color: var(--text2); font-size: 14px; line-height: 1.7; margin-bottom: 16px; }
        
        .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 1000; align-items: center; justify-content: center; }
        .modal.show { display: flex; }
        .modal-content { background: #000; border-radius: 16px; max-width: 90%; max-height: 90%; }
        .modal-header { padding: 14px 20px; background: #1a1a1a; display: flex; justify-content: space-between; }
        .modal-title { color: white; font-size: 14px; }
        .modal-close { background: var(--danger); color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; }
        
        @media (max-width: 1024px) { .stats-grid, .two-col, .settings-grid, .docs-layout { grid-template-columns: 1fr; } .nav-menu { display: none; } }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="nav-left">
            <div class="logo"><div class="logo-icon">S</div>Screenpipe</div>
            <div class="nav-menu">
                <div class="nav-item active" onclick="show('dashboard')">Dashboard</div>
                <div class="nav-item" onclick="show('recordings')">Recordings</div>
                <div class="nav-item" onclick="show('settings')">Settings</div>
                <div class="nav-item" onclick="show('docs')">Docs</div>
            </div>
        </div>
        <div class="user-avatar">SE</div>
    </nav>
    
    <main class="main">
        <div id="page-dashboard" class="page active">
            <div class="page-header"><h1>Welcome back! 👋</h1><p>Here's your recordings overview.</p></div>
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-icon" style="background:#fff7ed;color:var(--primary)">🎬</div><div class="stat-value">{{ recs|length }}</div><div class="stat-label">Total Recordings</div></div>
                <div class="stat-card"><div class="stat-icon" style="background:#ecfdf5;color:var(--success)">💾</div><div class="stat-value">{{ "%.1f"|format(size/1024) }}</div><div class="stat-label">KB Storage</div></div>
                <div class="stat-card"><div class="stat-icon" style="background:#eff6ff;color:#3b82f6">📅</div><div class="stat-value">{{ today }}</div><div class="stat-label">Today's</div></div>
                <div class="stat-card"><div class="stat-icon" style="background:#f5f3ff;color:#8b5cf6">⏱️</div><div class="stat-value">0</div><div class="stat-label">Hours</div></div>
            </div>
            <div class="two-col">
                <div>
                    <div class="card" style="margin-bottom:20px">
                        <div class="card-header"><span class="card-title">🎥 Control Center</span></div>
                        <div class="card-body">
                            <button class="record-btn {{ 'recording' if run else '' }}" onclick="toggle()">{{ '⏹ Stop' if run else '⏺ Start' }} Recording</button>
                            <div style="margin-top:12px"><div class="status-badge"><div class="status-dot {{ 'active' if run else '' }}"></div>{{ 'Recording...' if run else 'Ready' }}</div></div>
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-header"><span class="card-title">📹 Recent Recordings</span></div>
                        <div class="card-body">
                            {% if recs %}
                            <div class="rec-list">
                                {% for r in recs[:5] %}
                                <div class="rec-item">
                                    <div class="rec-thumb" onclick="play('{{ r.name }}')">▶</div>
                                    <div class="rec-info"><div class="rec-name">{{ r.name }}</div><div class="rec-meta">{{ (r.sz/1024/1024)|round(2) }} MB • {{ r.dt }}</div></div>
                                    <div class="rec-actions">
                                        <button class="rec-btn play" onclick="play('{{ r.name }}')">▶</button>
                                        <button class="rec-btn dl" onclick="dl('{{ r.name }}')">↓</button>
                                        <button class="rec-btn del" onclick="del('{{ r.name }}')">✕</button>
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                            {% else %}
                            <div class="empty">No recordings yet<br><small>Click "Start Recording" to begin</small></div>
                            {% endif %}
                        </div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><span class="card-title">🤖 AI Assistant</span></div>
                    <div class="card-body">
                        <div class="chat-messages" id="chatBox"><div class="chat-msg ai">Hi! Ask me anything.</div></div>
                        <div class="chat-input"><input type="text" id="chatInput" placeholder="Type..." onkeypress="if(event.key=='Enter')chat()"><button onclick="chat()">Send</button></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="page-recordings" class="page">
            <div class="page-header"><h1>Recordings</h1><p>All your recordings.</p></div>
            <div class="card"><div class="card-body">
                {% if recs %}
                <div class="rec-list">
                    {% for r in recs %}
                    <div class="rec-item">
                        <div class="rec-thumb" onclick="play('{{ r.name }}')">▶</div>
                        <div class="rec-info"><div class="rec-name">{{ r.name }}</div><div class="rec-meta">{{ (r.sz/1024/1024)|round(2) }} MB • {{ r.dt }}</div></div>
                        <div class="rec-actions"><button class="rec-btn play" onclick="play('{{ r.name }}')">Play</button><button class="rec-btn dl" onclick="dl('{{ r.name }}')">Save</button><button class="rec-btn del" onclick="del('{{ r.name }}')">Delete</button></div>
                    </div>
                    {% endfor %}
                </div>
                {% else %}<div class="empty">No recordings found</div>{% endif %}
            </div></div>
        </div>
        
        <div id="page-settings" class="page">
            <div class="page-header"><h1>Settings</h1><p>Customize your experience.</p></div>
            <div class="settings-grid">
                <div class="card"><div class="card-header"><span class="card-title">Recording</span></div><div class="card-body">
                    <div class="form-group"><label class="form-label">Quality</label><select class="form-select" id="q" onchange="save('quality',this.value)"><option value="720p">720p</option><option value="1080p">1080p</option><option value="1440p">1440p</option></select></div>
                    <div class="form-group"><label class="form-label">FPS</label><select class="form-select" id="f" onchange="save('fps',this.value)"><option value="15">15</option><option value="30">30</option><option value="60">60</option></select></div>
                    <label class="form-check"><input type="checkbox" id="a" {{ 'checked' if aud }} onchange="save('audio',this.checked)"><span>Record Audio</span></label>
                </div></div>
                <div class="card"><div class="card-header"><span class="card-title">AI & Storage</span></div><div class="card-body">
                    <label class="form-check"><input type="checkbox" id="aiEn" {{ 'checked' if ai }} onchange="save('ai_enabled',this.checked)"><span>AI Assistant</span></label>
                    <div class="form-group" style="margin-top:16px"><label class="form-label">Auto-delete</label><select class="form-select" id="del" onchange="save('auto_delete_days',this.value)"><option value="7">7 days</option><option value="30">30 days</option><option value="0">Never</option></select></div>
                </div></div>
            </div>
        </div>
        
        <div id="page-docs" class="page">
            <div class="page-header"><h1>Documentation</h1></div>
            <div class="docs-layout">
                <div class="docs-sidebar">
                    <div class="docs-link active" onclick="doc('intro')">Getting Started</div>
                    <div class="docs-link" onclick="doc('install')">Installation</div>
                    <div class="docs-link" onclick="doc('api')">API</div>
                    <div class="docs-link" onclick="doc('about')">About</div>
                </div>
                <div class="docs-content">
                    <div id="doc-intro" class="docs-section active">
                        <h2>Welcome to Screenpipe</h2>
                        <p>Modern screen recording dashboard. Capture, manage, and chat with AI.</p>
                    </div>
                    <div id="doc-install" class="docs-section">
                        <h2>Installation</h2>
                        <pre style="background:#1e293b;color:#e2e8f0;padding:16px;border-radius:12px;font-size:12px">git clone https://github.com/salaheddine-ezzahraoui/screenpipe_app.git
cd screenpipe_app
pip install flask requests
python3 app.py</pre>
                        <p>Open <strong>http://localhost:1112</strong></p>
                    </div>
                    <div id="doc-api" class="docs-section">
                        <h2>API Reference</h2>
                        <p><code>/</code> Dashboard &nbsp; <code>/start</code> Start &nbsp; <code>/stop</code> Stop<br><code>/video/x</code> Stream &nbsp; <code>/download/x</code> Download &nbsp; <code>/api/delete</code> Delete</p>
                    </div>
                    <div id="doc-about" class="docs-section">
                        <h2>About</h2>
                        <p><strong>Salaheddine Ezzahraoui</strong> - Founder<br>Azure Cloud & System Admin<br>Linux & Windows Expert</p>
                        <p>📧 salaheddine.ezzahraoui1@gmail.com<br>🐙 github.com/salaheddine-ezzahraoui</p>
                    </div>
                </div>
            </div>
        </div>
    </main>
    
    <div class="modal" id="modal">
        <div class="modal-content">
            <div class="modal-header"><span class="modal-title" id="vname"></span><button class="modal-close" onclick="closeVideo()">Close</button></div>
            <video id="vdo" controls style="max-height:70vh"></video>
        </div>
    </div>
    
    <script>
        let running = {{ 'true' if run else 'false' }};
        
        function show(p) {
            document.querySelectorAll('.page').forEach(x => x.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(x => x.classList.remove('active'));
            document.getElementById('page-'+p).classList.add('active');
            event.target.classList.add('active');
        }
        function doc(id) {
            document.querySelectorAll('.docs-section').forEach(x => x.classList.remove('active'));
            document.querySelectorAll('.docs-link').forEach(x => x.classList.remove('active'));
            document.getElementById('doc-'+id).classList.add('active');
            event.target.classList.add('active');
        }
        
        function toggle() { fetch(running?'/stop':'/start',{method:'POST'}).then(()=>location.reload()); }
        function play(n) { document.getElementById('vname').textContent=n; document.getElementById('vdo').src='/video/'+encodeURIComponent(n); document.getElementById('modal').classList.add('show'); }
        function closeVideo() { document.getElementById('modal').classList.remove('show'); document.getElementById('vdo').pause(); }
        function dl(n) { window.open('/download/'+encodeURIComponent(n),'_blank'); }
        function del(n) { if(confirm('Delete '+n+'?'))fetch('/api/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({filename:n})}).then(r=>r.json()).then(d=>d.success&&location.reload()); }
        function chat() {
            let m = document.getElementById('chatInput').value.trim();
            if(!m) return;
            let b = document.getElementById('chatBox');
            b.innerHTML += '<div class="chat-msg user">'+m+'</div><div class="chat-msg ai">...</div>';
            document.getElementById('chatInput').value = '';
            b.scrollTop = b.scrollHeight;
            fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})}).then(r=>r.json()).then(d=>{ b.lastElementChild.textContent=d.response||'No response'; b.scrollTop=b.scrollHeight; });
        }
        function save(k,v) { fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:k,value:v})}); }
        document.getElementById('modal').addEventListener('click',function(e){ if(e.target===this)closeVideo(); });
    </script>
</body>
</html>
"""

def get_recs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return sorted([{"name": os.path.basename(f), "sz": os.stat(f).st_size, "dt": datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%b %d, %H:%M")} for f in glob.glob(os.path.join(OUTPUT_DIR, "*.mp4"))], key=lambda x: x["dt"], reverse=True)

@app.route("/")
def index():
    load_config()
    recs = get_recs()
    return render_template_string(HTML, run=is_run(), recs=recs, size=sum(r["sz"] for r in recs), today=sum(1 for r in recs if datetime.now().strftime("%b %d") in r["dt"]), q=CONFIG.get("quality","1080p"), f=int(CONFIG.get("fps",30)), aud=CONFIG.get("audio",True), ai=CONFIG.get("ai_enabled",True), d=int(CONFIG.get("auto_delete_days",30)))

@app.route("/start", methods=["POST"])
def start():
    if not is_run():
        try: subprocess.Popen([SCRIPT, "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass
    return "", 204

@app.route("/stop", methods=["POST"])
def stop():
    try: subprocess.Popen([SCRIPT, "stop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass
    return "", 204

@app.route("/video/<path:filename>")
def video(filename):
    return send_file(os.path.join(OUTPUT_DIR, filename), mimetype="video/mp4") if os.path.exists(os.path.join(OUTPUT_DIR, filename)) else "Not found", 404

@app.route("/download/<path:filename>")
def download(filename):
    return send_file(os.path.join(OUTPUT_DIR, filename), as_attachment=True) if os.path.exists(os.path.join(OUTPUT_DIR, filename)) else "Not found", 404

@app.route("/api/delete", methods=["POST"])
def delete():
    try:
        os.remove(os.path.join(OUTPUT_DIR, request.json.get("filename","")))
        return jsonify({"success": True})
    except: return jsonify({"success": False}), 400

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        r = requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "prompt": f"{FOUNDER}\n\nUser: {request.json.get('message','')}", "stream": False}, timeout=180)
        return jsonify({"response": r.json().get("response", "")})
    except: return jsonify({"response": "AI unavailable"}), 500

@app.route("/api/settings", methods=["POST"])
def settings():
    d = request.json
    if d.get("key") in CONFIG:
        CONFIG[d["key"]] = d.get("value")
        save_config()
    return jsonify({"ok": True})

def is_run():
    try: return os.path.exists("/tmp/screenpipe_recording.pid") and os.kill(int(open("/tmp/screenpipe_recording.pid").read().strip()), 0) is None
    except: return False

if __name__ == "__main__":
    print("Screenpipe → http://localhost:1112")
    app.run(host="0.0.0.0", port=1112, debug=False)