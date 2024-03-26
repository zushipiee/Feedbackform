from flask import *
import csv

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form['name']
    gender = request.form['gender']
    email = request.form['email']
    comments = request.form['comments']
    rating = request.form['rating']

    with open('feedback.csv', 'a', newline='') as csvfile:
        fieldnames = ['Name', 'Gender', 'Email', 'Comments', 'Rating']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'Name': name, 'Gender': gender, 'Email': email, 'Comments': comments, 'Rating':rating})

    return render_template('success.html')

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 80, debug = False)
