from flask import Flask

app = Flask(__name__)

@app.route("/")
# Python Decorator that Flask uses to connect URL endpoints with code contained in functions. Argument to @app.route defines the URL's path component, which is the root path ("/") in the case
def index():
    return "Fuck You"

if __name__ == '__main__':
    app.run(host= '127.0.0.1', port= 8080, debug= True)