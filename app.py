from flask import Flask, send_from_directory, render_template_string
import os

app = Flask(__name__)

# LOGO FIX DA - Root la irunthalum work aagum da!
@app.route('/logo.png')
def logo():
    return send_from_directory('.', 'logo.png')

@app.route('/static/<path:filename>')
def static_files(filename):
    # static folder iruntha anga thedum, illa root la thedum da
    if os.path.exists(os.path.join('static', filename)):
        return send_from_directory('static', filename)
    else:
        return send_from_directory('.', filename)

@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Study World Hostel</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial; text-align: center; background: #f5f5f5; margin:0; padding:0; }
            .header { background: #1e3a8a; color: white; padding: 20px; }
            .logo { width: 120px; height: 120px; border-radius: 50%; background: white; padding: 5px; margin: 10px; }
            .card { background: white; margin: 20px; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .btn { background: #1e3a8a; color: white; padding: 12px 25px; border: none; border-radius: 5px; text-decoration: none; display: inline-block; margin: 10px; }
        </style>
    </head>
    <body>
        <div class="header">
            <img src="/logo.png" class="logo" alt="Logo" onerror="this.src='https://via.placeholder.com/120?text=LOGO'">
            <h1>🏨 Study World Hostel</h1>
            <p>Your Second Home for Studies</p>
        </div>
        <div class="card">
            <h2>Welcome Mapla! 🙏</h2>
            <p>Hostel Management System Live da!</p>
            <a href="#" class="btn">View Rooms</a>
            <a href="#" class="btn">Book Now</a>
        </div>
        <div class="card">
            <h3>📍 Facilities</h3>
            <p>✅ WiFi | ✅ Food | ✅ Study Room | ✅ 24/7 Security</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    """
