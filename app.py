from flask import *
from cryptography.fernet import Fernet
import csv

key = Fernet.generate_key()
with open('static/key.key', 'wb') as key_file:
    key_file.write(key)

def is_valid_fernet_token(token, cipher_suite):
    try:
        cipher_suite.decrypt(token.encode())
        return True
    except:
        return False

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

    with open('static/key.key', 'rb') as key_file:
        key = key_file.read()

    f = Fernet(key)

    name = f.encrypt(name.encode('utf-8')).decode()
    gender = f.encrypt(gender.encode('utf-8')).decode()
    email = f.encrypt(email.encode('utf-8')).decode()
    comments = f.encrypt(comments.encode('utf-8')).decode()
    rating = f.encrypt(rating.encode('utf-8')).decode()

    print(name)
    print(f.decrypt(name).decode('utf-8'))
    print(f.decrypt(gender).decode('utf-8'))
    print(f.decrypt(email).decode('utf-8'))
    print(f.decrypt(comments).decode('utf-8'))
    print(f.decrypt(rating).decode('utf-8'))

    with open('static/feedback.csv', 'a', newline='') as csvfile:
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

    # Load the key
    with open('static/key.key', 'rb') as key_file:
        key = key_file.read()

    f = Fernet(key)
    # Read feedback data from CSV file
    feedback_data = []
    with open('static/feedback.csv', 'r') as csvfile:
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

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 80, debug = False)
