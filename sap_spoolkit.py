print 'start'


from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World -- this is working !!!!"


import webbrowser
webbrowser.open('http://localhost:9090/', new = 2)


if __name__ == "__main__":
#    app = create_app(config.DATABASE_URI, debug=True)
    app.run(port=9090)



