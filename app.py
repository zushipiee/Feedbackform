from flask import *
from cryptography.fernet import Fernet
import csv
import os

##File Path
base_dir = os.path.abspath(os.path.dirname(__file__))
key_file_path = os.path.join(base_dir, 'static', 'key.key')
responce_file_path = os.path.join(base_dir, 'static', 'feedback.csv')

##Generate Key
key = Fernet.generate_key()

##Write Key into key.key
with open(key_file_path, 'wb') as key_file:
    key_file.write(key)

##Check Encryted data is valid/invalid
def is_valid_fernet_token(token, cipher_suite):
    try:
        cipher_suite.decrypt(token.encode())
        return True
    except:
        return False

##Flask Server
app = Flask(__name__)
app.secret_key = 'abcdefgabcdabcdabcd'

##HomePage
@app.route('/')
def index():
    return render_template('index.html')

##Process feedback and store to file
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form['name']
    gender = request.form['gender']
    email = request.form['email']
    comments = request.form['comments']
    rating = request.form['rating']

    with open(key_file_path) as key_file:
        key = key_file.read()

    f = Fernet(key)

    name = f.encrypt(name.encode('utf-8')).decode()
    gender = f.encrypt(gender.encode('utf-8')).decode()
    email = f.encrypt(email.encode('utf-8')).decode()
    comments = f.encrypt(comments.encode('utf-8')).decode()
    rating = f.encrypt(rating.encode('utf-8')).decode()

    with open(responce_file_path, 'a', newline='') as csvfile:
        fieldnames = ['Name', 'Gender', 'Email', 'Comments', 'Rating']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'Name': name, 'Gender': gender, 'Email': email, 'Comments': comments, 'Rating':rating})

    return render_template('success.html')

##Admin Login
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

##Retrive Feedback
@app.route('/admin_feedback')
def admin_feedback():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    # Load the key
    with open(key_file_path, 'rb') as key_file:
        key = key_file.read()

    f = Fernet(key)
    # Read feedback data from CSV file
    feedback_data = []
    with open(responce_file_path, 'r') as csvfile:
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
                for key in mapped_row:
                    try:
                        mapped_row[key] = f.decrypt(mapped_row[key].encode()).decode('utf-8')
                    except:
                        mapped_row[key] = 'Invalid token'

                feedback_data.append(mapped_row)

    print(feedback_data)  # Debugging output

    return render_template('admin_feedback.html', feedback_data=feedback_data)

##Run Program
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 80, debug = False)
