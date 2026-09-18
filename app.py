from flask import Flask, request, session, redirect
import sqlite3, os, random
from datetime import timedelta
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'hostel123'
app.permanent_session_lifetime = timedelta(days=30)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
DB='hostel.db'

def top(s):
    return f"""
    <html><head><meta name='viewport' content='width=device-width, initial-scale=1'>
    <style>button:active{{transform:scale(0.95)}}</style>
    </head>
    <body style='font-family:sans-serif; background:#e3f2fd; margin:0;'>
    <div style='max-width:550px; margin:auto; background:#fff; padding:20px; border-radius:15px; margin-top:15px; box-shadow:0 4px 15px rgba(0,0,0,0.1);'>
    <div style='display:flex; align-items:center; justify-content:space-between; margin-bottom:15px; border-bottom:2px solid #e3f2fd; padding-bottom:10px;'>
        <a href='javascript:history.back()' style='text-decoration:none; background:#e3f2fd; color:#0D47A1; padding:8px 15px; border-radius:20px; font-weight:bold; border:1px solid #0D47A1;'>⬅️ Back</a>
        <a href='/' style='text-decoration:none; background:#0D47A1; color:#fff; padding:8px 15px; border-radius:20px; font-weight:bold;'>🏠 Home</a>
    </div>
    <center><h2 style='color:#0D47A1; margin-top:0;'>STUDY WORLD HOSTEL</h2></center>
    {s}
    </div></body></html>
    """

def init_db():
    conn=sqlite3.connect(DB); c=conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT, roll TEXT UNIQUE, room TEXT, parent TEXT UNIQUE, photo TEXT, year TEXT, dept TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS wardens (id INTEGER PRIMARY KEY, name TEXT, year TEXT, mobile TEXT, username TEXT UNIQUE, password TEXT, status TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS gate_staff (id INTEGER PRIMARY KEY, name TEXT, mobile TEXT, username TEXT UNIQUE, password TEXT, status TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS outpass (id INTEGER PRIMARY KEY, roll TEXT, reason TEXT, from_date TEXT, to_date TEXT, status TEXT, photo TEXT, year TEXT, dept TEXT)")
    conn.commit(); conn.close()
init_db()

@app.route('/')
def home():
    if 'warden' in session: return redirect('/warden')
    if 'gate' in session: return redirect('/gate')
    if 'student' in session: return redirect('/student')
    if 'admin' in session: return redirect('/admin')
    return top("""
    <h3 style='text-align:center;'>DASHBOARD</h3>
    <a href='/student_login' style='text-decoration:none;'><div style='background:#0D47A1; color:#fff; padding:15px; border-radius:10px; text-align:center; margin-top:15px; font-weight:bold;'>🎓 Student</div></a>
    <a href='/warden_login' style='text-decoration:none;'><div style='background:#1565C0; color:#fff; padding:15px; border-radius:10px; text-align:center; margin-top:10px; font-weight:bold;'>👨‍🏫 Warden</div></a>
    <a href='/gate_login' style='text-decoration:none;'><div style='background:#2E7D32; color:#fff; padding:15px; border-radius:10px; text-align:center; margin-top:10px; font-weight:bold;'>🔐 Gate Security</div></a>
    <a href='/admin_login' style='text-decoration:none;'><div style='background:#000; color:#fff; padding:15px; border-radius:10px; text-align:center; margin-top:10px; font-weight:bold;'>⚙️ Admin</div></a>
    """)

@app.route('/student_register', methods=['GET','POST'])
def student_register():
    if request.method=='POST':
        name=request.form.get('name'); roll=request.form.get('roll'); room=request.form.get('room'); parent=request.form.get('parent'); year=request.form.get('year'); dept=request.form.get('dept')
        conn=sqlite3.connect(DB); c=conn.cursor()
        check=c.execute("SELECT * FROM students WHERE parent=? OR roll=?", (parent, roll)).fetchone()
        if check:
            conn.close()
            return top(f"<h3 style='color:red;'>❌ Already Exists!</h3><p>Mobile {parent} / Roll {roll} already irukku! One Mobile=One Account!</p><a href='/student_login'><button style='width:100%; padding:12px; background:#0D47A1; color:#fff; border:none; border-radius:8px;'>Login Pannu</button></a>")
        f=request.files.get('photo'); photo_name=""
        if f and f.filename!="":
            photo_name=secure_filename(roll+"_"+f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_name))
        c.execute("INSERT INTO students (name,roll,room,parent,photo,year,dept) VALUES (?,?,?,?,?,?,?)",(name,roll,room,parent,photo_name,year,dept))
        conn.commit(); conn.close()
        session.permanent=True; session['student']=roll; return redirect('/student')
    return top("""
    <h3>Student Register (Year/Dept/Photo)</h3>
    <form method='POST' enctype='multipart/form-data'>
    <input name='name' placeholder='Full Name' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:1px solid #ccc;' required>
    <input name='roll' placeholder='Roll No' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:1px solid #ccc;' required>
    <input name='year' placeholder='Year Ex: 2nd Year' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:2px solid #0D47A1;' required>
    <input name='dept' placeholder='Department Ex: CSE' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:2px solid #0D47A1;' required>
    <input name='room' placeholder='Room No' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:1px solid #ccc;' required>
    <input name='parent' placeholder='Parent Mobile * One=One Account' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:2px solid red;' required>
    <label style='margin-top:10px; display:block; font-weight:bold;'>Photo *</label>
    <input type='file' name='photo' accept='image/*' style='width:100%; padding:10px; margin-top:5px; border:1px solid #ccc; border-radius:8px;' required>
    <button style='width:100%; padding:14px; background:#0D47A1; color:#fff; margin-top:15px; border:none; border-radius:10px; font-weight:bold;'>Register</button>
    </form>
    """)

@app.route('/student_login', methods=['GET','POST'])
def student_login():
    if request.method=='POST':
        roll=request.form.get('roll'); conn=sqlite3.connect(DB); c=conn.cursor()
        r=c.execute("SELECT * FROM students WHERE roll=?", (roll,)).fetchone(); conn.close()
        if r: session.permanent=True; session['student']=roll; return redirect('/student')
    return top("<h3>Student Login</h3><form method='POST'><input name='roll' placeholder='Roll No' style='width:100%; padding:12px; border-radius:8px; border:1px solid #ccc;'><button style='width:100%; padding:12px; background:#0D47A1; color:#fff; margin-top:10px; border:none; border-radius:8px;'>Login</button></form><br><a href='/student_register'>New? Register (Year/Dept/Photo)</a>")

@app.route('/student', methods=['GET','POST'])
def student():
    if 'student' not in session: return redirect('/')
    conn=sqlite3.connect(DB); c=conn.cursor()
    stu=c.execute("SELECT * FROM students WHERE roll=?", (session['student'],)).fetchone()
    if request.method=='POST':
        reason=request.form.get('reason'); from_d=request.form.get('from_date'); to_d=request.form.get('to_date')
        s_year=stu[6] if stu and len(stu)>6 else ''; s_dept=stu[7] if stu and len(stu)>7 else ''
        c.execute("INSERT INTO outpass (roll,reason,from_date,to_date,status,photo,year,dept) VALUES (?,?,?,?,?,?,?,?)",(session['student'],reason,from_d,to_d,'Pending',stu[5] if stu else '', s_year, s_dept))
        conn.commit()
    rows=c.execute("SELECT * FROM outpass WHERE roll=?", (session['student'],)).fetchall(); conn.close()
    img=f"<center><img src='/static/uploads/{stu[5]}' style='width:100px; height:100px; object-fit:cover; border-radius:50%; border:3px solid #0D47A1;'></center>" if stu and stu[5] else ""
    y_d=f"<center><b>{stu[6]} - {stu[7]}</b> | Room: {stu[3]}</center>" if stu and len(stu)>7 else ""
    t="".join([f"<tr><td>{r[2]}</td><td>{r[3]}<br>to<br>{r[4]}</td><td>{r[5]}</td></tr>" for r in rows])
    return top(f"<h3>Student: {session['student']}</h3>{img}{y_d}<form method='POST' style='margin-top:15px;'><label style='font-weight:bold;'>Reason</label><input name='reason' placeholder='Ex: Going Home' style='width:100%; padding:12px; margin-top:5px; border-radius:8px; border:1px solid #ccc;' required><label style='margin-top:12px; display:block; font-weight:bold;'>FROM Date</label><input name='from_date' type='date' style='width:100%; padding:12px; margin-top:5px; border-radius:8px;' required><label style='margin-top:12px; display:block; font-weight:bold;'>TO Date</label><input name='to_date' type='date' style='width:100%; padding:12px; margin-top:5px; border-radius:8px;' required><button style='width:100%; padding:14px; background:#0D47A1; color:#fff; margin-top:15px; border:none; border-radius:10px; font-weight:bold;'>Apply Outpass (From-To)</button></form><h4>My Requests</h4><table border=1 style='width:100%; border-collapse:collapse;'><tr style='background:#e3f2fd;'><th>Reason</th><th>From-To</th><th>Status</th></tr>{t}</table><br><a href='/logout'>Logout</a>")

@app.route('/warden_register', methods=['GET','POST'])
def warden_register():
    if request.method=='POST':
        name=request.form.get('name'); year=request.form.get('year'); mobile=request.form.get('mobile'); user=request.form.get('username'); pwd=request.form.get('password')
        conn=sqlite3.connect(DB); c=conn.cursor()
        try: c.execute("INSERT INTO wardens (name,year,mobile,username,password,status) VALUES (?,?,?,?,?,?)",(name,year,mobile,user,pwd,'WAITING')); conn.commit()
        except: return top("<h3 style='color:red;'>Username Exists!</h3><a href='/warden_register'>Back</a>")
        conn.close(); return top("<h3 style='color:orange;'>Waiting for Admin Approval! ✅</h3><a href='/'><button style='width:100%; padding:12px; background:#000; color:#fff; border:none; border-radius:8px;'>Go Dashboard</button></a>")
    return top("<h3>Warden Register</h3><form method='POST'><input name='name' placeholder='Full Name' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:1px solid #ccc;' required><input name='year' placeholder='Which Year Warden? Ex: 2nd Year' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:1px solid #ccc;' required><input name='mobile' placeholder='Mobile' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:1px solid #ccc;' required><input name='username' placeholder='Create Username' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:1px solid #ccc;' required><input name='password' type='password' placeholder='Create Password' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:1px solid #ccc;' required><button style='width:100%; padding:14px; background:#1565C0; color:#fff; margin-top:10px; border:none; border-radius:10px;'>Submit to Admin</button></form>")

@app.route('/warden_login', methods=['GET','POST'])
def warden_login():
    if request.method=='POST':
        u=request.form.get('username'); p=request.form.get('password'); conn=sqlite3.connect(DB); c=conn.cursor()
        r=c.execute("SELECT * FROM wardens WHERE username=? AND password=? AND status='APPROVED'",(u,p)).fetchone(); conn.close()
        if r: session.permanent=True; session['warden']=r[0]; return redirect('/warden')
        else: return top("<p style='color:red;'>❌ Not Approved or Wrong Password!</p><a href='/warden_login'>Back</a>")
    return top("<h3>Warden Login</h3><form method='POST'><input name='username' placeholder='Username' style='width:100%; padding:12px; border-radius:8px; border:1px solid #ccc;'><input name='password' type='password' placeholder='Password' style='width:100%; padding:12px; margin-top:10px; border-radius:8px; border:1px solid #ccc;'><button style='width:100%; padding:12px; background:#1565C0; color:#fff; margin-top:10px; border:none; border-radius:8px;'>Login</button></form><br><a href='/warden_register'>New? Register</a><br><a href='/warden_forgot' style='color:red; font-weight:bold;'>Forgot Password? OTP</a>")

@app.route('/warden')
def warden():
    if 'warden' not in session: return redirect('/')
    conn=sqlite3.connect(DB); c=conn.cursor()
    rows=c.execute("SELECT outpass.*, students.photo FROM outpass JOIN students ON outpass.roll=students.roll WHERE outpass.status='Pending'").fetchall(); conn.close()
    t="".join([f"<tr><td>{r[1]}<br><small style='background:#0D47A1; color:#fff; padding:2px 6px; border-radius:5px;'>{r[7]}-{r[8]}</small><br><img src='/static/uploads/{r[6]}' width='50' style='border-radius:50%; margin-top:5px;'></td><td>{r[2]}<br><b style='color:#0D47A1;'>{r[3]} to {r[4]}</b></td><td><a href='/approve/{r[0]}'><button style='background:green; color:#fff; padding:8px; border:none; border-radius:5px;'>Approve</button></a></td></tr>" for r in rows])
    return top(f"<h3>Warden Dashboard</h3><table border=1 style='width:100%; border-collapse:collapse;'><tr style='background:#e3f2fd;'><th>Student (Year-Dept)</th><th>Reason & From-To</th><th>Action</th></tr>{t}</table><br><a href='/logout'><button style='width:100%; padding:10px; background:#ccc; border:none; border-radius:8px;'>Logout</button></a>")

@app.route('/approve/<id>')
def approve(id):
    conn=sqlite3.connect(DB); c=conn.cursor(); c.execute("UPDATE outpass SET status='Approved' WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect('/warden')

@app.route('/warden_forgot', methods=['GET','POST'])
def warden_forgot():
    if request.method=='POST':
        user=request.form.get('username'); mobile=request.form.get('mobile')
        conn=sqlite3.connect(DB); c=conn.cursor(); r=c.execute("SELECT * FROM wardens WHERE username=? AND mobile=?", (user,mobile)).fetchone(); conn.close()
        if r: otp=str(random.randint(1000,9999)); session['warden_otp']=otp; session['warden_reset_user']=user; return redirect('/warden_verify_otp')
        return top("<h3 style='color:red;'>Not Match!</h3><a href='/warden_forgot'>Try Again</a>")
    return top("<h3>Warden Forgot - OTP</h3><form method='POST'><input name='username' placeholder='Username' style='width:100%; padding:12px;' required><input name='mobile' placeholder='Registered Mobile' style='width:100%; padding:12px; margin-top:8px;' required><button style='width:100%; padding:12px; background:#1565C0; color:#fff; margin-top:10px;'>Send OTP</button></form>")

@app.route('/warden_verify_otp', methods=['GET','POST'])
def warden_verify_otp():
    if 'warden_otp' not in session: return redirect('/warden_forgot')
    if request.method=='POST':
        if request.form.get('otp')==session.get('warden_otp'):
            user=session.get('warden_reset_user'); conn=sqlite3.connect(DB); c=conn.cursor()
            c.execute("UPDATE wardens SET password=? WHERE username=?", (request.form.get('new_password'), user)); conn.commit(); conn.close()
            session.pop('warden_otp', None); session.pop('warden_reset_user', None)
            return top("<h3 style='color:green;'>✅ Reset Success!</h3><a href='/warden_login'><button style='width:100%; padding:12px; background:#1565C0; color:#fff;'>Login Now</button></a>")
        else: return top(f"<h3 style='color:red;'>Wrong OTP! Correct: {session.get('warden_otp')}</h3><a href='/warden_verify_otp'>Try Again</a>")
    return top(f"<h3>Verify OTP - Warden</h3><p style='background:yellow; padding:10px; text-align:center; border-radius:8px;'><b>DEMO OTP: {session.get('warden_otp')}</b></p><form method='POST'><input name='otp' placeholder='Enter OTP' style='width:100%; padding:12px;' required><input name='new_password' type='password' placeholder='New Password' style='width:100%; padding:12px; margin-top:8px;' required><button style='width:100%; padding:12px; background:green; color:#fff; margin-top:10px;'>Verify & Reset</button></form>")

@app.route('/gate_register', methods=['GET','POST'])
def gate_register():
    if request.method=='POST':
        name=request.form.get('name'); mobile=request.form.get('mobile'); user=request.form.get('username'); pwd=request.form.get('password')
        conn=sqlite3.connect(DB); c=conn.cursor()
        try: c.execute("INSERT INTO gate_staff (name,mobile,username,password,status) VALUES (?,?,?,?,?)",(name,mobile,user,pwd,'WAITING')); conn.commit()
        except: return top("<h3 style='color:red;'>Username Exists!</h3><a href='/gate_register'>Back</a>")
        conn.close(); return top("<h3 style='color:orange;'>Gate Waiting for Admin!</h3><a href='/'><button style='width:100%; padding:12px; background:#000; color:#fff; border:none; border-radius:8px;'>Dashboard</button></a>")
    return top("<h3>Gate Security Register</h3><form method='POST'><input name='name' placeholder='Full Name' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:1px solid #ccc;' required><input name='mobile' placeholder='Mobile' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:1px solid #ccc;' required><input name='username' placeholder='Create Username' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:1px solid #ccc;' required><input name='password' type='password' placeholder='Create Password' style='width:100%; padding:12px; margin-top:8px; border-radius:8px; border:1px solid #ccc;' required><button style='width:100%; padding:14px; background:#2E7D32; color:#fff; margin-top:10px; border:none; border-radius:10px;'>Submit to Admin</button></form>")

@app.route('/gate_login', methods=['GET','POST'])
def gate_login():
    if request.method=='POST':
        u=request.form.get('username'); p=request.form.get('password'); conn=sqlite3.connect(DB); c=conn.cursor()
        r=c.execute("SELECT * FROM gate_staff WHERE username=? AND password=? AND status='APPROVED'",(u,p)).fetchone(); conn.close()
        if r: session.permanent=True; session['gate']=r[0]; return redirect('/gate')
        else: return top("<p style='color:red;'>❌ Not Approved or Wrong Password!</p><a href='/gate_login'>Back</a>")
    return top("<h3>Gate Security Login</h3><form method='POST'><input name='username' placeholder='Username' style='width:100%; padding:12px; border-radius:8px; border:1px solid #ccc;'><input name='password' type='password' placeholder='Password' style='width:100%; padding:12px; margin-top:10px; border-radius:8px; border:1px solid #ccc;'><button style='width:100%; padding:12px; background:#2E7D32; color:#fff; margin-top:10px; border:none; border-radius:8px;'>Login</button></form><br><a href='/gate_register'>New? Register</a><br><a href='/gate_forgot' style='color:red; font-weight:bold;'>Forgot Password? OTP</a>")

@app.route('/gate')
def gate():
    if 'gate' not in session: return redirect('/')
    conn=sqlite3.connect(DB); c=conn.cursor()
    rows=c.execute("SELECT * FROM outpass WHERE status='Approved'").fetchall()
    t="".join([f"<tr><td>{r[1]}<br><small>{r[7]}-{r[8]}</small></td><td>{r[2]}<br><b>{r[3]} to {r[4]}</b></td><td><a href='/allow/{r[0]}'><button style='background:green; color:#fff; padding:8px; border:none; border-radius:5px;'>ALLOW</button></a></td></tr>" for r in rows])
    rows2=c.execute("SELECT * FROM outpass WHERE status='Outside'").fetchall()
    t2="".join([f"<tr><td>{r[1]}<br><small>{r[7]}-{r[8]}</small></td><td>{r[2]}</td><td><a href='/returned/{r[0]}'><button>RETURNED</button></a></td></tr>" for r in rows2]); conn.close()
    return top(f"<h3>Gate - Year/Dept/From-To</h3><table border=1 style='width:100%; border-collapse:collapse;'><tr style='background:#c8e6c9;'><th>Roll (Year-Dept)</th><th>Reason & From-To</th><th>Action</th></tr>{t}</table><h3 style='margin-top:20px;'>Outside</h3><table border=1 style='width:100%; border-collapse:collapse;'><tr style='background:#ffccbc;'><th>Roll</th><th>Details</th><th>Action</th></tr>{t2}</table><br><a href='/logout'><button style='width:100%; padding:10px; background:#ccc; border:none; border-radius:8px;'>Logout</button></a>")

@app.route('/allow/<id>')
def allow(id):
    conn=sqlite3.connect(DB); c=conn.cursor(); c.execute("UPDATE outpass SET status='Outside' WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect('/gate')
@app.route('/returned/<id>')
def returned(id):
    conn=sqlite3.connect(DB); c=conn.cursor(); c.execute("UPDATE outpass SET status='Returned' WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect('/gate')

@app.route('/gate_forgot', methods=['GET','POST'])
def gate_forgot():
    if request.method=='POST':
        user=request.form.get('username'); mobile=request.form.get('mobile')
        conn=sqlite3.connect(DB); c=conn.cursor(); r=c.execute("SELECT * FROM gate_staff WHERE username=? AND mobile=?", (user,mobile)).fetchone(); conn.close()
        if r: otp=str(random.randint(1000,9999)); session['gate_otp']=otp; session['gate_reset_user']=user; return redirect('/gate_verify_otp')
        return top("<h3 style='color:red;'>Not Match!</h3><a href='/gate_forgot'>Try Again</a>")
    return top("<h3>Gate Forgot - OTP</h3><form method='POST'><input name='username' placeholder='Username' style='width:100%; padding:12px;' required><input name='mobile' placeholder='Registered Mobile' style='width:100%; padding:12px; margin-top:8px;' required><button style='width:100%; padding:12px; background:#2E7D32; color:#fff; margin-top:10px;'>Send OTP</button></form>")

@app.route('/gate_verify_otp', methods=['GET','POST'])
def gate_verify_otp():
    if 'gate_otp' not in session: return redirect('/gate_forgot')
    if request.method=='POST':
        if request.form.get('otp')==session.get('gate_otp'):
            user=session.get('gate_reset_user'); conn=sqlite3.connect(DB); c=conn.cursor()
            c.execute("UPDATE gate_staff SET password=? WHERE username=?", (request.form.get('new_password'), user)); conn.commit(); conn.close()
            session.pop('gate_otp', None); session.pop('gate_reset_user', None)
            return top("<h3 style='color:green;'>✅ Gate Reset Success!</h3><a href='/gate_login'><button style='width:100%; padding:12px; background:#2E7D32; color:#fff;'>Login Now</button></a>")
        else: return top(f"<h3 style='color:red;'>Wrong OTP! Correct: {session.get('gate_otp')}</h3><a href='/gate_verify_otp'>Try Again</a>")
    return top(f"<h3>Verify OTP - Gate</h3><p style='background:yellow; padding:10px; text-align:center; border-radius:8px;'><b>DEMO OTP: {session.get('gate_otp')}</b></p><form method='POST'><input name='otp' placeholder='Enter OTP' style='width:100%; padding:12px;' required><input name='new_password' type='password' placeholder='New Password' style='width:100%; padding:12px; margin-top:8px;' required><button style='width:100%; padding:12px; background:green; color:#fff; margin-top:10px;'>Verify & Reset</button></form>")

@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        if request.form.get('username')=='admin' and request.form.get('password')=='admin123':
            session.permanent=True; session['admin']=True; return redirect('/admin')
    return top("<h3>Admin Login</h3><form method='POST'><input name='username' placeholder='admin' style='width:100%; padding:12px;'><input name='password' type='password' placeholder='admin123' style='width:100%; padding:12px; margin-top:10px;'><button style='width:100%; padding:12px; background:#000; color:#fff; margin-top:10px;'>Login</button></form>")

@app.route('/admin')
def admin():
    if 'admin' not in session: return redirect('/')
    conn=sqlite3.connect(DB); c=conn.cursor()
    wardens=c.execute("SELECT * FROM wardens WHERE status='WAITING'").fetchall()
    gates=c.execute("SELECT * FROM gate_staff WHERE status='WAITING'").fetchall(); conn.close()
    w="".join([f"<tr><td>{r[1]} - {r[2]} Year<br><small>{r[3]}</small></td><td>{r[4]}</td><td><a href='/admin_approve_warden/{r[0]}'><button style='background:green; color:#fff; padding:8px; border:none; border-radius:5px;'>Approve</button></a></td></tr>" for r in wardens])
    g="".join([f"<tr><td>{r[1]}<br><small>{r[2]}</small></td><td>{r[3]}</td><td><a href='/admin_approve_gate/{r[0]}'><button style='background:green; color:#fff; padding:8px; border:none; border-radius:5px;'>Approve</button></a></td></tr>" for r in gates])
    return top(f"<h3>Admin - Approvals</h3><h4>Warden Waiting ({len(wardens)})</h4><table border=1 style='width:100%; border-collapse:collapse;'><tr><th>Name-Year</th><th>User</th><th>Action</th></tr>{w}</table><h4 style='margin-top:20px;'>Gate Waiting ({len(gates)})</h4><table border=1 style='width:100%; border-collapse:collapse;'><tr><th>Name</th><th>User</th><th>Action</th></tr>{g}</table><br><a href='/logout'><button style='width:100%; padding:10px; background:#ccc; border:none; border-radius:8px;'>Logout</button></a>")

@app.route('/admin_approve_warden/<id>')
def admin_approve_warden(id):
    conn=sqlite3.connect(DB); c=conn.cursor(); c.execute("UPDATE wardens SET status='APPROVED' WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect('/admin')
@app.route('/admin_approve_gate/<id>')
def admin_approve_gate(id):
    conn=sqlite3.connect(DB); c=conn.cursor(); c.execute("UPDATE gate_staff SET status='APPROVED' WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect('/admin')

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == '__main__': app.run(debug=True, host='0.0.0.0', port=5000)
