from flask import Flask, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('client.feed'))

if __name__ == '__main__':
    app.run(debug=True)
