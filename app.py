from flask import Flask, send_from_directory, render_template_string, request, redirect, session
import os, json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'study_world_hostel_2024_secure'

DATA_FILE = 'outpass_requests.json'

# Warden Credentials - Year Wise
WARDENS = {
    '1st': {'username': 'warden1', 'password': 'warden1@123', 'year': '1st Year'},
    '2nd': {'username': 'warden2', 'password': 'warden2@123', 'year': '2nd Year'},
    '3rd': {'username': 'warden3', 'password': 'warden3@123', 'year': '3rd Year'},
    'final': {'username': 'wardenfinal', 'password': 'wardenfinal@123', 'year': 'Final Year'}
}
GATE_USER = {'username': 'gate', 'password': 'gate@123'}
ADMIN_USER = {'username': 'admin', 'password': 'admin@123'}

def load_data():
    if not os.path.exists(DATA_FILE): return []
    try:
        with open(DATA_FILE, 'r') as f: return json.load(f)
    except: return []

def save_data(data):
    with open(DATA_FILE, 'w') as f: json.dump(data, f, indent=2)

@app.route('/logo.png')
def logo():
    return send_from_directory('.', 'logo.png')

@app.route('/static/<path:filename>')
def static_files(filename):
    if os.path.exists(os.path.join('static', filename)):
        return send_from_directory('static', filename)
    return send_from_directory('.', filename)

BASE_STYLE = """
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:'Segoe UI',Arial;margin:0;background:#f4f6f9;}
.header{background:#1e3a8a;color:white;padding:20px;text-align:center;}
.logo{width:80px;height:80px;border-radius:50%;background:white;padding:4px;}
.container{max-width:1100px;margin:20px auto;padding:15px;}
.card{background:white;padding:22px;border-radius:12px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,0.06);overflow-x:auto;}
.btn{background:#1e3a8a;color:white;padding:10px 18px;border:none;border-radius:6px;text-decoration:none;display:inline-block;margin:4px;cursor:pointer;}
.btn-green{background:#16a34a;} .btn-red{background:#dc2626;} .btn-grey{background:#475569;}
input,select,textarea{width:100%;padding:10px;margin:8px 0 14px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;}
table{width:100%;border-collapse:collapse;} th,td{padding:11px;border-bottom:1px solid #eee;text-align:left;font-size:14px;} th{background:#f8fafc;}
.badge{padding:4px 10px;border-radius:20px;font-size:12px;color:white;}
.badge-pending{background:#f59e0b;} .badge-approved{background:#16a34a;} .badge-rejected{background:#dc2626;} .badge-gate{background:#1e3a8a;}
</style>
"""

# HOME
@app.route('/')
def home():
    return render_template_string(f"""
    <html><head><title>Study World Hostel</title>{BASE_STYLE}</head><body>
    <div class="header"><img src="/logo.png" class="logo"><h1>Study World Hostel</h1><p>Hostel Management System</p></div>
    <div class="container">
        <div class="card" style="text-align:center;">
            <h2>Welcome</h2>
            <a href="/student/outpass" class="btn">Student - Apply Outpass</a>
            <a href="/student/status" class="btn btn-grey">Student - Check Outpass Status</a><br><br>
            <a href="/warden/login" class="btn btn-green">Warden Login</a>
            <a href="/gate/login" class="btn" style="background:#7c3aed;">Gate Security Login</a>
            <a href="/admin/login" class="btn btn-grey">Admin Login</a>
        </div>
        <div class="card"><h3>Warden Login Details</h3>
        <p><b>1st Year:</b> warden1 / warden1@123 | <b>2nd Year:</b> warden2 / warden2@123<br>
        <b>3rd Year:</b> warden3 / warden3@123 | <b>Final Year:</b> wardenfinal / wardenfinal@123<br>
        <b>Gate:</b> gate / gate@123 | <b>Admin:</b> admin / admin@123</p></div>
    </div></body></html>
    """)

# STUDENT OUTPASS APPLY
@app.route('/student/outpass', methods=['GET','POST'])
def student_outpass():
    if request.method == 'POST':
        data = load_data()
        new_id = len(data) + 1
        data.append({
            'id': new_id, 'name': request.form['name'], 'roll_no': request.form['roll_no'],
            'phone': request.form['phone'], 'year': request.form['year'],
            'reason': request.form['reason'], 'from_date': request.form['from_date'],
            'to_date': request.form['to_date'], 'status': 'Pending',
            'warden_status': 'Pending', 'gate_status': 'Not Allowed',
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        save_data(data)
        return render_template_string(f"<html><head>{BASE_STYLE}</head><body><div class='container'><div class='card' style='text-align:center;'><h2 style='color:green;'>Outpass Request Submitted</h2><p>Your Outpass ID: <b>{new_id}</b> - Year: {request.form['year']}</p><p>Check status using your phone number or roll number.</p><a href='/student/status' class='btn'>Check Status</a><a href='/' class='btn btn-grey'>Home</a></div></div></body></html>")
    
    return render_template_string(f"""
    <html><head><title>Student Outpass</title>{BASE_STYLE}</head><body>
    <div class="header"><img src="/logo.png" class="logo"><h2>Student Outpass Request</h2></div>
    <div class="container"><div class="card"><form method="POST">
    <label>Full Name</label><input name="name" required>
    <label>Roll Number</label><input name="roll_no" required>
    <label>Phone Number</label><input name="phone" required>
    <label>Year</label><select name="year" required>
        <option value="1st Year">1st Year</option><option value="2nd Year">2nd Year</option>
        <option value="3rd Year">3rd Year</option><option value="Final Year">Final Year</option>
    </select>
    <label>From Date</label><input type="date" name="from_date" required>
    <label>To Date</label><input type="date" name="to_date" required>
    <label>Reason for Outpass</label><textarea name="reason" rows="3" required></textarea>
    <button class="btn" style="width:100%;">Submit Outpass Request</button>
    </form></div></div></body></html>
    """)

# STUDENT CHECK STATUS
@app.route('/student/status', methods=['GET','POST'])
def student_status():
    result_html = ""
    if request.method == 'POST':
        search = request.form['search'].strip().lower()
        data = load_data()
        filtered = [r for r in data if search in r['phone'].lower() or search in r['roll_no'].lower() or search in r['name'].lower()]
        if not filtered:
            result_html = "<p style='text-align:center;color:red;'>No records found</p>"
        else:
            rows = ""
            for r in reversed(filtered):
                badge = "badge-pending" if r['status']=="Pending" else "badge-approved" if r['status']=="Approved" else "badge-rejected"
                gate_badge = "badge-approved" if r['gate_status']=="Allowed" else "badge-pending"
                rows += f"<tr><td>{r['id']}</td><td>{r['from_date']} to {r['to_date']}</td><td>{r['reason'][:30]}</td><td><span class='badge {badge}'>{r['status']}</span></td><td><span class='badge {gate_badge}'>{r['gate_status']}</span></td><td>{r['warden_status']}</td></tr>"
            result_html = f"<div class='card'><h3>Your Outpass History</h3><table><tr><th>ID</th><th>Date</th><th>Reason</th><th>Warden Status</th><th>Gate Status</th><th>Remarks</th></tr>{rows}</table></div>"
    
    return render_template_string(f"""
    <html><head><title>Check Status</title>{BASE_STYLE}</head><body>
    <div class="header"><img src="/logo.png" class="logo"><h2>Check Outpass Status</h2></div>
    <div class="container"><div class="card">
    <form method="POST"><label>Enter Phone / Roll No / Name</label><input name="search" placeholder="Ex: 98765 or 21CSE01" required>
    <button class="btn" style="width:100%;">Search</button></form></div>{result_html}
    <div style="text-align:center;"><a href="/" class="btn btn-grey">Home</a></div></div></body></html>
    """)

# WARDEN LOGIN
@app.route('/warden/login', methods=['GET','POST'])
def warden_login():
    if request.method == 'POST':
        uname = request.form['username']; pwd = request.form['password']
        for key, w in WARDENS.items():
            if w['username']==uname and w['password']==pwd:
                session['warden'] = key
                return redirect('/warden/dashboard')
        return "<h3 style='text-align:center;color:red;'>Invalid Credentials <a href='/warden/login'>Try Again</a></h3>"
    return render_template_string(f"""
    <html><head><title>Warden Login</title>{BASE_STYLE}</head><body>
    <div class="header" style="background:#16a34a;"><h2>Warden Login</h2></div>
    <div class="container"><div class="card" style="max-width:450px;margin:30px auto;">
    <form method="POST"><label>Username</label><input name="username" placeholder="warden1" required>
    <label>Password</label><input type="password" name="password" required>
    <button class="btn btn-green" style="width:100%;">Login</button></form>
    <p style="font-size:12px;margin-top:15px;">1st: warden1 / warden1@123<br>2nd: warden2 / warden2@123<br>3rd: warden3 / warden3@123<br>Final: wardenfinal / wardenfinal@123</p>
    </div></div></body></html>
    """)

@app.route('/warden/dashboard')
def warden_dashboard():
    if 'warden' not in session: return redirect('/warden/login')
    w_key = session['warden']; w_info = WARDENS[w_key]
    data = load_data()
    filtered = [r for r in data if r['year']==w_info['year']]
    rows = ""
    for r in reversed(filtered):
        actions = ""
        if r['status']=='Pending':
            actions = f"<a href='/warden/approve/{r['id']}' class='btn btn-green' style='padding:5px 10px;font-size:12px;'>Approve</a> <a href='/warden/reject/{r['id']}' class='btn btn-red' style='padding:5px 10px;font-size:12px;'>Reject</a>"
        else:
            actions = r['status']
        rows += f"<tr><td>{r['id']}</td><td>{r['name']}<br><small>{r['roll_no']}</small></td><td>{r['phone']}</td><td>{r['from_date']} to {r['to_date']}</td><td>{r['reason']}</td><td>{r['status']}</td><td>{actions}</td></tr>"
    if not rows: rows = f"<tr><td colspan='7' style='text-align:center;'>No requests for {w_info['year']}</td></tr>"
    return render_template_string(f"""
    <html><head><title>Warden Dashboard</title>{BASE_STYLE}</head><body>
    <div class="header" style="background:#16a34a;"><h2>{w_info['year']} - Warden Dashboard</h2><a href="/warden/logout" style="color:white;">Logout</a></div>
    <div class="container"><div class="card"><h3>Outpass Requests - {w_info['year']} ({len(filtered)})</h3>
    <table><tr><th>ID</th><th>Student</th><th>Phone</th><th>Date</th><th>Reason</th><th>Status</th><th>Action</th></tr>{rows}</table></div></div></body></html>
    """)

@app.route('/warden/approve/<int:id>')
def warden_approve(id):
    if 'warden' not in session: return redirect('/warden/login')
    data = load_data()
    for r in data:
        if r['id']==id:
            r['status']='Approved'; r['warden_status']=f"Approved by {WARDENS[session['warden']]['year']} Warden"
            r['gate_status']='Allowed'
    save_data(data)
    return redirect('/warden/dashboard')

@app.route('/warden/reject/<int:id>')
def warden_reject(id):
    if 'warden' not in session: return redirect('/warden/login')
    data = load_data()
    for r in data:
        if r['id']==id:
            r['status']='Rejected'; r['warden_status']=f"Rejected by {WARDENS[session['warden']]['year']} Warden"
            r['gate_status']='Not Allowed'
    save_data(data)
    return redirect('/warden/dashboard')

@app.route('/warden/logout')
def warden_logout():
    session.pop('warden', None); return redirect('/')

# GATE SECURITY
@app.route('/gate/login', methods=['GET','POST'])
def gate_login():
    if request.method == 'POST':
        if request.form['username']==GATE_USER['username'] and request.form['password']==GATE_USER['password']:
            session['gate']=True; return redirect('/gate/dashboard')
        return "<h3>Invalid Gate Credentials <a href='/gate/login'>Try Again</a></h3>"
    return render_template_string(f"""
    <html><head><title>Gate Login</title>{BASE_STYLE}</head><body>
    <div class="header" style="background:#7c3aed;"><h2>Gate Security Login</h2></div>
    <div class="container"><div class="card" style="max-width:450px;margin:auto;"><form method="POST">
    <label>Username</label><input name="username" value="gate"><label>Password</label><input type="password" name="password" required>
    <button class="btn" style="background:#7c3aed;width:100%;">Login</button><p style="font-size:12px;">gate / gate@123</p></form></div></div></body></html>
    """)

@app.route('/gate/dashboard')
def gate_dashboard():
    if not session.get('gate'): return redirect('/gate/login')
    data = load_data()
    approved = [r for r in data if r['status']=='Approved']
    rows = "".join([f"<tr><td>{r['id']}</td><td>{r['name']} ({r['roll_no']}) - {r['year']}</td><td>{r['phone']}</td><td>{r['from_date']} to {r['to_date']}</td><td><span class='badge badge-approved'>Allowed</span></td></tr>" for r in reversed(approved)]) or "<tr><td colspan='5' style='text-align:center;'>No approved outpasses</td></tr>"
    return render_template_string(f"""
    <html><head><title>Gate Dashboard</title>{BASE_STYLE}</head><body>
    <div class="header" style="background:#7c3aed;"><h2>Gate Security - Allowed List</h2><a href="/gate/logout" style="color:white;">Logout</a></div>
    <div class="container"><div class="card"><h3>Approved Outpasses - Allow at Gate</h3>
    <table><tr><th>ID</th><th>Student</th><th>Phone</th><th>Date</th><th>Gate Status</th></tr>{rows}</table></div></div></body></html>
    """)

@app.route('/gate/logout')
def gate_logout():
    session.pop('gate', None); return redirect('/')

# ADMIN
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username']==ADMIN_USER['username'] and request.form['password']==ADMIN_USER['password']:
            session['admin']=True; return redirect('/admin/dashboard')
        return "<h3>Invalid Admin Credentials</h3>"
    return render_template_string(f"""
    <html><head><title>Admin Login</title>{BASE_STYLE}</head><body>
    <div class="header"><h2>Admin Login</h2></div>
    <div class="container"><div class="card" style="max-width:400px;margin:auto;"><form method="POST">
    <input name="username" placeholder="admin"><input type="password" name="password" placeholder="admin@123">
    <button class="btn" style="width:100%;">Login</button></form></div></div></body></html>
    """)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'): return redirect('/admin/login')
    data = load_data()
    rows = "".join([f"<tr><td>{r['id']}</td><td>{r['name']}<br><small>{r['roll_no']} - {r['year']}</small></td><td>{r['phone']}</td><td>{r['from_date']} to {r['to_date']}</td><td>{r['status']}</td><td>{r['gate_status']}</td><td>{r['created_at']}</td></tr>" for r in reversed(data)]) or "<tr><td colspan='7'>No data</td></tr>"
    return render_template_string(f"""
    <html><head><title>Admin Dashboard</title>{BASE_STYLE}</head><body>
    <div class="header"><h2>Admin Dashboard - All Outpass Records</h2><a href="/admin/logout" style="color:white;">Logout</a> | <a href="/" style="color:white;">Home</a></div>
    <div class="container"><div class="card"><h3>Total Requests: {len(data)}</h3>
    <table><tr><th>ID</th><th>Student</th><th>Phone</th><th>Date</th><th>Warden Status</th><th>Gate Status</th><th>Created</th></tr>{rows}</table></div></div></body></html>
    """)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None); return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
