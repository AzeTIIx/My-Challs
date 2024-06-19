from flask import Flask, request, make_response, render_template, send_from_directory
import hashlib
import base64
import pickle
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
SECRET_KEY = os.environ.get('SECRET_KEY')

def sign_data(data):
    return hashlib.sha256((data + SECRET_KEY).encode()).hexdigest()

def serialize_data(data):
    return base64.b64encode(pickle.dumps(data)).decode()

def deserialize_data(data):
    return pickle.loads(base64.b64decode(data))

@app.route('/public/<path:path>')
def send_report(path):
    return send_from_directory('public', path)

@app.route('/')
def index():
    try:
        signed_cookie = request.cookies.get('signed_cookie')
        
        if signed_cookie:
            cookie_data, signature = signed_cookie.split('.')
            if hashlib.sha256((cookie_data + SECRET_KEY).encode()).hexdigest() == signature:
                result = deserialize_data(cookie_data)
                return render_template('success.html', result=result)
            else:
                return render_template('error.html', message="Signature invalide!"), 403
        else:
            initial_data = "You're either with us or against us"
            serialized_data = serialize_data(initial_data)
            signed_data = sign_data(serialized_data)
            signed_cookie_value = f"{serialized_data}.{signed_data}"
            response = make_response(render_template('welcome.html'))
            response.set_cookie('signed_cookie', signed_cookie_value)
            return response
    except Exception as e:
        return render_template('error.html', message=str(e)), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="Page non trouvée!"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', message="Erreur interne du serveur!"), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return render_template('error.html', message="Une erreur est survenue!"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
