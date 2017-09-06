"""

SpoolKit


"""
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello():
#    return "Hello World -- this is xx  working !!!!"
    return render_template('index.html')

# open up browser
import webbrowser
webbrowser.open('http://localhost:9090/', new = 2)


if __name__ == "__main__":
#    app = create_app(config.DATABASE_URI, debug=True)
    app.run(port=9090)



