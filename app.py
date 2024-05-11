from flask import *
import csv

app = Flask(__name__)
app.secret_key = 'abcdefgabcdabcdabcd'

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

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin01' and password == 'abc123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_feedback'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('admin_login.html')

@app.route('/admin_feedback')
def admin_feedback():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    # Read feedback data from CSV file
    feedback_data = []
    with open('feedback.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Assuming the order of columns is: Name, Gender, Email, Comments, Rating
            if len(row) >= 5:  # Check if the row has at least 5 columns
                mapped_row = {
                    'Name': row[0],       # First column
                    'Gender': row[1],     # Second column
                    'Email': row[2],      # Third column
                    'Comments': row[3],   # Fourth column
                    'Rating': row[4]      # Fifth column
                }
                feedback_data.append(mapped_row)

    print(feedback_data)  # Debugging output

    return render_template('admin_feedback.html', feedback_data=feedback_data)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 80, debug = False)
