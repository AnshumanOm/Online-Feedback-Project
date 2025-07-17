from flask import Flask, request, render_template, send_file, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv
from io import StringIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feedback.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # required for sessions

db = SQLAlchemy(app)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)

# Public: Feedback Form
@app.route('/feedback.html')
def feedback_form():
    return send_file('feedback.html')

# Store Feedback
@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    data = request.form
    fb = Feedback(name=data['name'], email=data['email'], rating=int(data['rating']), comments=data['comments'])
    db.session.add(fb)
    db.session.commit()
    return "Feedback submitted successfully!"

# Admin Login Page
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['username'] == 'Anshuman' and request.form['password'] == 'Anshuman29':
            session['admin_logged_in'] = True
            return redirect('/admin-dashboard')
        return "Invalid credentials!"
    return send_file('admin_login.html')

# Admin Dashboard
@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin-login')
    feedbacks = Feedback.query.all()
    avg_rating = round(db.session.query(db.func.avg(Feedback.rating)).scalar() or 0, 2)
    return render_template('admin_dashboard.html', feedbacks=feedbacks, total=len(feedbacks), avg_rating=avg_rating)

# Export CSV
@app.route('/export-feedback')
def export_feedback():
    feedbacks = Feedback.query.all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Email', 'Rating', 'Comments', 'Date Submitted'])
    for fb in feedbacks:
        writer.writerow([fb.name, fb.email, fb.rating, fb.comments, fb.date_submitted])
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment;filename=feedback.csv'
    }

# REST API: Return feedback as JSON
@app.route('/api/feedback')
def api_feedback():
    feedbacks = Feedback.query.all()
    return jsonify([{
        'name': f.name,
        'email': f.email,
        'rating': f.rating,
        'comments': f.comments,
        'date_submitted': f.date_submitted.strftime("%Y-%m-%d %H:%M:%S")
    } for f in feedbacks])

# Logout
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin-login')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
