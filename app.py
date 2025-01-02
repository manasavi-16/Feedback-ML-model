from flask import Flask, render_template, request, redirect, url_for, flash, session
import joblib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load models and vectorizer
usability_model = joblib.load('usability_model.pkl')
design_model = joblib.load('design_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123"

# List to store feedback data
feedback_list = []

# Positive and Negative Sentiment Keywords
POSITIVE_KEYWORDS = ["good", "nice", "very good", "best", "outstanding", "fantastic", "great", "excellent"]
NEGATIVE_KEYWORDS = ["bad", "poor", "very bad", "disappointed", "worst", "terrible"]

# Helper function to extract sentiment
def extract_sentiment(review_type):
    if review_type in POSITIVE_KEYWORDS:
        return "Positive"
    elif review_type in NEGATIVE_KEYWORDS:
        return "Negative"
    return "Neutral"

# Helper function to calculate product review sentiment
def calculate_product_review(sentiments):
    positive_count = sentiments.count("Positive")
    negative_count = sentiments.count("Negative")
    if positive_count > 3:
        return "Positive"
    elif negative_count > 3:
        return "Negative"
    return "Neutral"

# Main home page with options
@app.route('/')
def main_home():
    return render_template('home_page.html')

# Feedback form
@app.route('/feedback')
def feedback():
    return render_template('feedback_form.html')

# Process feedback
@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        suggestions = request.form.get('suggestions')

        # Sentiments for different aspects
        usability_review = extract_sentiment(request.form.get('usability_review'))
        design_review = extract_sentiment(request.form.get('design_review'))
        price_review = extract_sentiment(request.form.get('price_review'))
        sound_review = extract_sentiment(request.form.get('sound_quality_review'))
        battery_review = extract_sentiment(request.form.get('battery_life_review'))
        camera_review = extract_sentiment(request.form.get('camera_quality_review'))

        # Calculate overall product review
        sentiments = [usability_review, design_review, price_review, sound_review, battery_review, camera_review]
        product_review = calculate_product_review(sentiments)

        # Store feedback
        feedback_list.append({
            'name': name,
            'email': email,
            'phone': phone,
            'usability_sentiment': usability_review,
            'design_sentiment': design_review,
            'price_sentiment': price_review,
            'sound_sentiment': sound_review,
            'battery_life_sentiment': battery_review,
            'camera_sentiment': camera_review,
            'suggestions': suggestions,
            'product_review': product_review
        })

        return render_template('submission_confirmation.html')

# Admin login
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid username or password!")
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

# Admin dashboard
@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html', feedbacks=feedback_list)

# Admin logout
@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
