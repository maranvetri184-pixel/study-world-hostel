from flask import Flask, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "study_world_final_logo_2025"
DB = "hostel.db"

ADMIN_USER = "admin"; ADMIN_PASS = "Admin@2025"

# THANNI THANNI WARDEN LOGIN DA MAPLA
WARDENS = {
    "warden1": {"pass": "Warden1@2025", "year": "1st Year"},
    "warden2": {"pass": "Warden2@2025", "year": "2nd Year"},
    "warden3": {"pass": "Warden3@2025", "year": "3rd Year"},
    "warden4": {"pass": "Warden4@2025", "year": "4th Year"},
}
GATE_USER = "gate"; GATE_PASS = "Gate@2025"

def init_db():
    conn=sqlite3.connect(DB); c=conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS outpass (id INTEGER PRIMARY KEY, roll TEXT, name TEXT, year TEXT, out_date TEXT, out_time TEXT, in_date TEXT, reason TEXT, status TEXT DEFAULT 'Pending', created_at TEXT)")
    conn.commit(); conn.close()
init_db()

top = """
<style>
body{font-family:Arial; margin:0; background:#eef2f7}
.bar{background:#0c1a5c; color:white; padding:10px 20px; font-weight:bold; font-size:18px; display:flex; align-items:center; gap:12px}
.bar img{height:45px; width:45px; background:white; border-radius:50%; padding:3px; object-fit:contain}
.box{max-width:1000px; margin:25px auto; background:white; padding:25px; border-radius:12px; box-shadow:0 4px 12px #0002}
input,select,textarea,button{padding:12px; width:100%; margin:6px 0; border-radius:6px; border:1px solid #ccc; box-sizing:border-box; font-size:14px}
button{background:#0c1a5c; color:white; font-weight:bold; cursor:pointer; border:none}
table{width:100%; border-collapse:collapse; font-size:11px; margin-top:10px}
th,td{border:1px solid #ccc; padding:6px; text-align:center}
th{background:#0c1a5c; color:white}
</style>
<div class=bar><img src="/static/logo.png"><span>STUDY WORLD HOSTEL</span><span style="font-size:12px; font-weight:normal; margin-left:auto">Secure Pass System</span></div>
"""

@app.route('/', methods=['GET','POST'])
def home():
    if request.method=='POST':
        roll=request.form['roll'].strip().upper()
        conn=sqlite3.connect(DB); c=conn.cursor()
        if c.execute("SELECT * FROM outpass WHERE roll=? AND status IN ('Pending','Approved') LIMIT 1",(roll,)).fetchone():
            conn.close(); return top+f"<div class=box><h2 style='color:red'>❌ {roll} Already Applied!</h2><a href='/'>Back</a></div>"
        c.execute("INSERT INTO outpass (roll,name,year,out_date,out_time,in_date,reason,created_at) VALUES (?,?,?,?,?,?,?,?)",(roll,request.form['name'],request.form['year'],request.form['out_date'],request.form['out_time'],request.form['in_date'],request.form['reason'],datetime.now().strftime("%d-%m-%Y %H:%M")))
        conn.commit(); conn.close(); return top+f"<div class=box><h2 style='color:green'>✅ Applied Successfully!</h2><a href='/'>Home</a></div>"
    return top+'''
    <div class=box><h2>Student Outpass - One Time Only</h2>
    <form method=post>
    <input name=roll placeholder="Roll No" required>
    <input name=name placeholder="Name" required>
    <select name=year required><option value="">Select Year</option><option>1st Year</option><option>2nd Year</option><option>3rd Year</option><option>4th Year</option></select>
    <input type=date name=out_date required>
    <input type=time name=out_time required>
    <input type=date name=in_date required>
    <textarea name=reason placeholder="Reason for Outpass" required></textarea>
    <button>Submit Request</button>
    </form><br><hr><br>
    <a href="/admin"><button style="background:#b00">👑 ADMIN LOGIN</button></a><br><br>
    <a href="/warden"><button style="background:#333">Warden Login</button></a><br><br>
    <a href="/gate"><button style="background:#1a7a1a">Gate Login</button></a>
    </div>'''

@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method=='POST' and 'approve' not in request.form and 'reject' not in request.form and 'delete' not in request.form:
        if request.form.get('username','').strip()==ADMIN_USER and request.form.get('password','').strip()==ADMIN_PASS: session['admin']=True
        else: return top+"<div class=box><h3 style='color:red'>❌ Invalid Admin!</h3><a href='/admin'>Back</a></div>"
    if 'admin' not in session: return top+'<div class=box><h3>ADMIN LOGIN</h3><form method=post><input name=username placeholder="admin" required><input name=password type=password placeholder="Password" required><button style="background:#b00">Login</button></form></div>'
    conn=sqlite3.connect(DB); c=conn.cursor()
    if 'approve' in request.form: c.execute("UPDATE outpass SET status='Approved' WHERE id=?",(request.form['approve'],)); conn.commit()
    if 'reject' in request.form: c.execute("UPDATE outpass SET status='Rejected' WHERE id=?",(request.form['reject'],)); conn.commit()
    if 'delete' in request.form: c.execute("DELETE FROM outpass WHERE id=?",(request.form['delete'],)); conn.commit()
    rows=c.execute("SELECT * FROM outpass ORDER BY id DESC").fetchall()
    t="".join([f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]} {r[5]}</td><td>{r[8]}</td><td><form method=post style='display:flex; gap:3px'><button name=approve value={r[0]} style='background:green; width:35px'>OK</button><button name=reject value={r[0]} style='background:orange; width:35px'>X</button><button name=delete value={r[0]} style='background:red; width:35px'>Del</button></form></td></tr>" for r in rows]) if rows else ""
    table=f"<table><tr><th>ID</th><th>Roll</th><th>Name</th><th>Year</th><th>Out</th><th>Status</th><th>Action</th></tr>{t}</table>" if rows else "<p>No Data</p>"
    conn.close(); return top+f"<div class=box><h2>👑 ADMIN - All Students</h2>{table}<br><a href='/logout'>Logout</a></div>"

@app.route('/warden', methods=['GET','POST'])
def warden():
    if request.method=='POST' and 'approve' not in request.form and 'reject' not in request.form:
        u=request.form.get('username','').strip()
        p=request.form.get('password','').strip()
        if u in WARDENS and WARDENS[u]['pass']==p:
            session['warden']=True; session['warden_user']=u; session['warden_year']=WARDENS[u]['year']
        else: return top+"<div class=box><h3 style='color:red'>❌ Invalid Warden!</h3><a href='/warden'>Back</a></div>"
    if 'warden' not in session: return top+'<div class=box><h3>Warden Login - Year Wise</h3><form method=post><input name=username placeholder="warden1 / warden2 / warden3 / warden4" required><input name=password type=password placeholder="Password" required><button>Login</button></form></div>'
    conn=sqlite3.connect(DB); c=conn.cursor()
    if 'approve' in request.form: c.execute("UPDATE outpass SET status='Approved' WHERE id=?",(request.form['approve'],)); conn.commit()
    if 'reject' in request.form: c.execute("UPDATE outpass SET status='Rejected' WHERE id=?",(request.form['reject'],)); conn.commit()
    year_filter=session.get('warden_year')
    rows=c.execute("SELECT * FROM outpass WHERE year=? ORDER BY id DESC",(year_filter,)).fetchall()
    t="".join([f"<tr><td>{r[1]}</td><td>{r[2]}</td><td>{r[4]} {r[5]}</td><td>{r[8]}</td><td><form method=post><button name=approve value={r[0]} style='background:green; width:35px'>OK</button><button name=reject value={r[0]} style='background:red; width:35px'>X</button></form></td></tr>" for r in rows]) if rows else ""
    table=f"<table><tr><th>Roll</th><th>Name</th><th>Out</th><th>Status</th><th>Action</th></tr>{t}</table>" if rows else "<p>No Data for this year</p>"
    conn.close(); return top+f"<div class=box><h2>Warden Panel - {year_filter} ({session.get('warden_user')})</h2>{table}<br><a href='/logout'>Logout</a></div>"

@app.route('/gate', methods=['GET','POST'])
def gate():
    if request.method=='POST' and 'username' in request.form:
        if request.form.get('username','').strip()==GATE_USER and request.form.get('password','').strip()==GATE_PASS: session['gate']=True
        else: return top+"<div class=box><h3 style='color:red'>❌ Invalid Gate!</h3><a href='/gate'>Back</a></div>"
    if 'gate' not in session: return top+'<div class=box><h3>Gate Login</h3><form method=post><input name=username placeholder="gate" required><input name=password type=password placeholder="Password" required><button>Login</button></form></div>'
    conn=sqlite3.connect(DB); c=conn.cursor()
    rows=c.execute("SELECT * FROM outpass WHERE status='Approved' ORDER BY id DESC").fetchall()
    t="".join([f"<tr><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]} {r[5]}</td><td style='color:green; font-weight:bold'>ALLOWED</td></tr>" for r in rows]) if rows else "<tr><td colspan=5>No Approved Students</td></tr>"
    table=f"<table><tr><th>Roll</th><th>Name</th><th>Year</th><th>Out Time</th><th>Status</th></tr>{t}</table>"
    conn.close(); return top+f"<div class=box><h2>🚪 Gate - Approved List (No Roll Check Needed)</h2>{table}<br><br><a href='/logout'>Logout</a></div>"

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
