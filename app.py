import os
import json
from datetime import datetime
from flask import Flask, send_from_directory, render_template_string, request, redirect, session

app = Flask(__name__)
app.secret_key = 'study_world_hostel_secure_2026'

OUTPASS_FILE = 'outpass_requests.json'
USERS_FILE = 'users.json'
RESET_FILE = 'reset_requests.json'

DEFAULT_WARDENS = {
    'warden1': {'password': 'Warden1@2024', 'year': '1st Year', 'mobile': '9876543210'},
    'warden2': {'password': 'Warden2@2024', 'year': '2nd Year', 'mobile': '9876543211'},
    'warden3': {'password': 'Warden3@2024', 'year': '3rd Year', 'mobile': '9876543212'},
    'wardenfinal': {'password': 'Final@2024', 'year': 'Final Year', 'mobile': '9876543213'}
}

def load_json(file):
    if not os.path.exists(file):
        return []
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return []

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

def load_users():
    users = load_json(USERS_FILE)
    if not users:
        default_list = []
        for uname, info in DEFAULT_WARDENS.items():
            default_list.append({
                'id': len(default_list)+1, 'username': uname, 'password': info['password'],
                'role': 'warden', 'year': info['year'], 'mobile': info['mobile'], 'status': 'Active'
            })
        default_list.append({'id':5,'username':'admin','password':'Admin@2024','role':'admin','year':'All','mobile':'9999999999','status':'Active'})
        default_list.append({'id':6,'username':'gate','password':'Gate@2024','role':'gate','year':'All','mobile':'8888888888','status':'Active'})
        save_json(USERS_FILE, default_list)
        return default_list
    return users

@app.route('/logo.png')
def logo():
    return send_from_directory('.', 'logo.png')

BASE = """
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial;margin:0;background:#f4f6f9;}
.header{background:#1e3a8a;color:white;padding:18px;text-align:center;}
.logo{width:75px;height:75px;border-radius:50%;background:white;padding:4px;}
.container{max-width:1100px;margin:18px auto;padding:12px;}
.card{background:white;padding:20px;border-radius:12px;margin-bottom:18px;box-shadow:0 2px 6px rgba(0,0,0,0.05);overflow-x:auto;}
.btn{background:#1e3a8a;color:white;padding:9px 16px;border:none;border-radius:6px;text-decoration:none;display:inline-block;margin:3px;cursor:pointer;}
.btn-green{background:#16a34a;} .btn-red{background:#dc2626;} .btn-grey{background:#475569;}
input,select,textarea{width:100%;padding:10px;margin:7px 0 12px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;}
table{width:100%;border-collapse:collapse;} th,td{padding:10px;border-bottom:1px solid #eee;font-size:14px;text-align:left;} th{background:#f8fafc;}
</style>
"""

@app.route('/')
def home():
    return render_template_string(f"<html><head><title>Study World Hostel</title>{BASE}</head><body><div class='header'><img src='/logo.png' class='logo'><h1>Study World Hostel</h1><p>Outpass Management System</p></div><div class='container'><div class='card' style='text-align:center;'><a href='/student/outpass' class='btn'>Student - Apply Outpass</a><a href='/student/status' class='btn btn-grey'>Check Status</a><br><br><a href='/login' class='btn btn-green'>Warden / Gate / Admin Login</a><a href='/register' class='btn'>Create New Account</a><a href='/forgot-password' class='btn btn-grey'>Forgot Password?</a></div></div></body></html>")

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        uname = request.form['username'].strip()
        if any(u['username']==uname for u in users):
            return "<h3 style='text-align:center;color:red;'>Username already exists <a href='/register'>Try again</a></h3>"
        users.append({'id': len(users)+1, 'username': uname, 'password': request.form['password'],'role': request.form['role'], 'year': request.form.get('year','All'),'mobile': request.form['mobile'], 'status': 'Active' if request.form['role']!='admin' else 'Pending'})
        save_json(USERS_FILE, users)
        return f"<div style='text-align:center;padding:40px;font-family:Arial;'><h3 style='color:green;'>Account Created! Username: {uname}</h3><a href='/login'>Login Now</a></div>"
    return render_template_string(f"<html><head><title>Register</title>{BASE}</head><body><div class='header'><h2>Create Account</h2></div><div class='container'><div class='card' style='max-width:500px;margin:auto;'><form method='POST'><label>Username</label><input name='username' required><label>Mobile Number (for password recovery)</label><input name='mobile' pattern='[0-9]{{10}}' required><label>Role</label><select name='role' required><option value='gate'>Gate Security</option><option value='admin'>Admin</option><option value='warden'>Warden</option></select><label>Year</label><select name='year'><option>1st Year</option><option>2nd Year</option><option>3rd Year</option><option>Final Year</option><option>All</option></select><label>Password</label><input type='password' name='password' required><button class='btn' style='width:100%;'>Create Account</button></form></div></div></body></html>")

@app.route('/forgot-password', methods=['GET','POST'])
def forgot_password():
    if request.method == 'POST':
        users = load_users()
        uname = request.form['username']; mobile = request.form['mobile']; newpass = request.form['new_password']
        user = next((u for u in users if u['username']==uname and u['mobile']==mobile), None)
        if not user:
            return "<h3 style='text-align:center;color:red;'>Username and Mobile not matching <a href='/forgot-password'>Try again</a></h3>"
        if user['role']=='warden':
            resets = load_json(RESET_FILE)
            resets.append({'id':len(resets)+1,'username':uname,'mobile':mobile,'new_password':newpass,'status':'Pending','date':datetime.now().strftime("%Y-%m-%d %H:%M")})
            save_json(RESET_FILE, resets)
            return "<div style='text-align:center;padding:40px;font-family:Arial;'><h3 style='color:orange;'>Password reset request sent to Admin for approval</h3><a href='/'>Home</a></div>"
        else:
            user['password']=newpass
            save_json(USERS_FILE, users)
            return "<div style='text-align:center;padding:40px;font-family:Arial;'><h3 style='color:green;'>Password Changed Successfully</h3><a href='/login'>Login Now</a></div>"
    return render_template_string(f"<html><head><title>Forgot Password</title>{BASE}</head><body><div class='header'><h2>Forgot Password - Via Mobile</h2></div><div class='container'><div class='card' style='max-width:500px;margin:auto;'><form method='POST'><label>Username</label><input name='username' required><label>Registered Mobile</label><input name='mobile' required><label>New Password</label><input type='password' name='new_password' required><button class='btn' style='width:100%;'>Reset Password</button><p style='font-size:12px;'>Warden needs Admin permission</p></form></div></div></body></html>")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        uname = request.form['username']; pwd = request.form['password']
        user = next((u for u in users if u['username']==uname and u['password']==pwd and u['status']=='Active'), None)
        if not user:
            return "<h3 style='text-align:center;color:red;'>Invalid login <a href='/login'>Try again</a></h3>"
        session['user']=user
        if user['role']=='warden': return redirect('/warden/dashboard')
        elif user['role']=='gate': return redirect('/gate/dashboard')
        else: return redirect('/admin/dashboard')
    return render_template_string(f"<html><head><title>Login</title>{BASE}</head><body><div class='header'><h2>Login</h2></div><div class='container'><div class='card' style='max-width:450px;margin:auto;'><form method='POST'><label>Username</label><input name='username' required><label>Password</label><input type='password' name='password' required><button class='btn' style='width:100%;'>Login</button></form><br><a href='/forgot-password'>Forgot Password?</a></div></div></body></html>")

@app.route('/student/outpass', methods=['GET','POST'])
def student_outpass():
    if request.method == 'POST':
        data = load_json(OUTPASS_FILE)
        data.append({'id':len(data)+1,'name':request.form['name'],'roll_no':request.form['roll_no'],'phone':request.form['phone'],'year':request.form['year'],'reason':request.form['reason'],'from_date':request.form['from_date'],'to_date':request.form['to_date'],'status':'Pending','gate_status':'Not Allowed','returned':'No','created_at':datetime.now().strftime("%Y-%m-%d %H:%M")})
        save_json(OUTPASS_FILE, data)
        return f"<div style='text-align:center;padding:40px;font-family:Arial;'><h2>Outpass ID {len(data)} Submitted for {request.form['year']}</h2><a href='/student/status'>Check Status</a></div>"
    return render_template_string(f"<html><head><title>Outpass</title>{BASE}</head><body><div class='header'><img src='/logo.png' class='logo'><h2>Student Outpass</h2></div><div class='container'><div class='card' style='max-width:600px;margin:auto;'><form method='POST'><label>Name</label><input name='name' required><label>Roll No</label><input name='roll_no' required><label>Phone</label><input name='phone' required><label>Year</label><select name='year' required><option>1st Year</option><option>2nd Year</option><option>3rd Year</option><option>Final Year</option></select><label>From</label><input type='date' name='from_date' required><label>To</label><input type='date' name='to_date' required><label>Reason</label><textarea name='reason' required></textarea><button class='btn' style='width:100%;'>Submit</button></form></div></div></body></html>")

@app.route('/student/status', methods=['GET','POST'])
def student_status():
    html_result=""
    if request.method=='POST':
        search=request.form['search'].lower()
        data=load_json(OUTPASS_FILE)
        filtered=[r for r in data if search in r['phone'].lower() or search in r['roll_no'].lower()]
        rows="".join([f"<tr><td>{r['id']}</td><td>{r['from_date']} to {r['to_date']}</td><td>{r['status']}</td><td>{r['gate_status']}</td><td>{r['returned']}</td></tr>" for r in reversed(filtered)]) or "<tr><td colspan='5'>No records</td></tr>"
        html_result=f"<div class='card'><table><tr><th>ID</th><th>Date</th><th>Warden Status</th><th>Gate</th><th>Returned?</th></tr>{rows}</table></div>"
    return render_template_string(f"<html><head><title>Status</title>{BASE}</head><body><div class='header'><h2>Check Outpass Status</h2></div><div class='container'><div class='card' style='max-width:600px;margin:auto;'><form method='POST'><input name='search' placeholder='Phone or Roll No' required><button class='btn' style='width:100%;'>Search</button></form></div>{html_result}<div style='text-align:center;'><a href='/' class='btn btn-grey'>Home</a></div></div></body></html>")

@app.route('/warden/dashboard')
def warden_dashboard():
    if 'user' not in session or session['user']['role']!='warden': return redirect('/login')
    w=session['user']; data=load_json(OUTPASS_FILE)
    filtered=[r for r in data if r['year']==w['year']]
    rows="".join([f"<tr><td>{r['id']}</td><td>{r['name']}<br><small>{r['roll_no']}</small></td><td>{r['phone']}</td><td>{r['from_date']} to {r['to_date']}</td><td>{r['reason']}</td><td>{r['status']}</td><td>{f'<a href=/warden/approve/{r[\"id\"]} class=btn btn-green style=padding:4px 8px;font-size:12px>Approve</a> <a href=/warden/reject/{r[\"id\"]} class=btn btn-red style=padding:4px 8px;font-size:12px>Reject</a>' if r['status']=='Pending' else r['status']}</td></tr>" for r in reversed(filtered)]) or f"<tr><td colspan='7'>No requests for {w['year']}</td></tr>"
    return render_template_string(f"<html><head>{BASE}</head><body><div class='header' style='background:#16a34a;'><h2>{w['year']} Warden - {w['username']}</h2><a href='/logout' style='color:white;'>Logout</a></div><div class='container'><div class='card'><h3>Requests ({len(filtered)})</h3><table><tr><th>ID</th><th>Student</th><th>Phone</th><th>Date</th><th>Reason</th><th>Status</th><th>Action</th></tr>{rows}</table></div></div></body></html>")

@app.route('/warden/approve/<int:id>')
def warden_approve(id):
    if 'user' not in session: return redirect('/login')
    data=load_json(OUTPASS_FILE)
    for r in data:
        if r['id']==id: r['status']='Approved'; r['gate_status']='Allowed'
    save_json(OUTPASS_FILE, data); return redirect('/warden/dashboard')

@app.route('/warden/reject/<int:id>')
def warden_reject(id):
    if 'user' not in session: return redirect('/login')
    data=load_json(OUTPASS_FILE)
    for r in data:
        if r['id']==id: r['status']='Rejected'; r['gate_status']='Not Allowed'
    save_json(OUTPASS_FILE, data); return redirect('/warden/dashboard')

@app.route('/gate/dashboard')
def gate_dashboard():
    if 'user' not in session or session['user']['role']!='gate': return redirect('/login')
    data=load_json(OUTPASS_FILE)
    approved=[r for r in data if r['status']=='Approved']
    rows="".join([f"<tr><td>{r['id']}</td><td>{r['name']} ({r['roll_no']}) {r['year']}</td><td>{r['phone']}</td><td>{r['from_date']} to {r['to_date']}</td><td>{r['returned']}</td><td>{f'<a href=/gate/returned/{r[\"id\"]} class=btn btn-green style=padding:4px 8px>Mark Returned</a>' if r['returned']=='No' else 'Returned'}</td></tr>" for r in reversed(approved)]) or "<tr><td colspan='6'>No approved</td></tr>"
    return render_template_string(f"<html><head>{BASE}</head><body><div class='header' style='background:#7c3aed;'><h2>Gate Security - Returned View</h2><a href='/logout' style='color:white;'>Logout</a></div><div class='container'><div class='card'><h3>Approved - College to Hostel</h3><table><tr><th>ID</th><th>Student</th><th>Phone</th><th>Date</th><th>Returned</th><th>Action</th></tr>{rows}</table></div></div></body></html>")

@app.route('/gate/returned/<int:id>')
def gate_returned(id):
    if 'user' not in session: return redirect('/login')
    data=load_json(OUTPASS_FILE)
    for r in data:
        if r['id']==id: r['returned']='Yes - '+datetime.now().strftime("%Y-%m-%d %H:%M")
    save_json(OUTPASS_FILE, data); return redirect('/gate/dashboard')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' not in session or session['user']['role']!='admin': return redirect('/login')
    users=load_users(); outpass=load_json(OUTPASS_FILE); resets=load_json(RESET_FILE)
    user_rows="".join([f"<tr><td>{u['id']}</td><td>{u['username']}</td><td>{u['role']}</td><td>{u['year']}</td><td>{u['mobile']}</td><td>{u['status']}</td></tr>" for u in users])
    out_rows="".join([f"<tr><td>{r['id']}</td><td>{r['name']} {r['year']}</td><td>{r['status']}</td><td>{r['gate_status']}</td><td>{r['returned']}</td></tr>" for r in reversed(outpass[-20:])])
    reset_rows="".join([f"<tr><td>{r['id']}</td><td>{r['username']}</td><td>{r['mobile']}</td><td>{r['status']}</td><td><a href='/admin/approve-reset/{r['id']}' class='btn btn-green' style='padding:4px 8px;'>Approve</a></td></tr>" for r in resets if r['status']=='Pending']) or "<tr><td colspan='5'>No pending requests</td></tr>"
    return render_template_string(f"<html><head>{BASE}</head><body><div class='header'><h2>Admin Dashboard</h2><a href='/logout' style='color:white;'>Logout</a></div><div class='container'><div class='card'><h3>Password Reset Requests</h3><table><tr><th>ID</th><th>Username</th><th>Mobile</th><th>Status</th><th>Action</th></tr>{reset_rows}</table></div><div class='card'><h3>All Users - Passwords Hidden</h3><table><tr><th>ID</th><th>Username</th><th>Role</th><th>Year</th><th>Mobile</th><th>Status</th></tr>{user_rows}</table></div><div class='card'><h3>Recent Outpass</h3><table><tr><th>ID</th><th>Student</th><th>Warden</th><th>Gate</th><th>Returned</th></tr>{out_rows}</table></div></div></body></html>")

@app.route('/admin/approve-reset/<int:id>')
def admin_approve_reset(id):
    if 'user' not in session or session['user']['role']!='admin': return redirect('/login')
    resets=load_json(RESET_FILE); users=load_users()
    for r in resets:
        if r['id']==id and r['status']=='Pending':
            r['status']='Approved'
            for u in users:
                if u['username']==r['username'] and u['mobile']==r['mobile']:
                    u['password']=r['new_password']
    save_json(RESET_FILE, resets); save_json(USERS_FILE, users)
    return redirect('/admin/dashboard')

@app.route('/logout')
def logout():
    session.clear(); return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
