from flask import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('homepage.html')

if __name__ == '__main__':
    app.run(port=8080)