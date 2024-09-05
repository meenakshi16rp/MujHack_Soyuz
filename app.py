from flask import Flask, render_template, request, redirect, url_for, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import googlemaps  # For Google Maps API integration

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r"C:/Users/Rakesh Pai/Downloads/disaster-response-website-firebase-adminsdk-yc5xg-8b4244dec6.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Initialize Google Maps Client (Replace with your Google Maps API Key)
gmaps = googlemaps.Client(key='YOUR_GOOGLE_MAPS_API_KEY')

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to check report
@app.route('/check_report', methods=['GET', 'POST'])
def check_report():
    if request.method == 'POST':
        city = request.form['city']
        # Fetch reports based on city from Firestore
        reports = db.collection('emergencies').where('location', '==', city).stream()
        incidents = [{'id': report.id, 'data': report.to_dict()} for report in reports]

        # Obtain coordinates of the city for Google Maps
        geocode_result = gmaps.geocode(city)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
        else:
            location = {'lat': 0, 'lng': 0}  # Default location if city not found

        return render_template('check_report.html', incidents=incidents, city=city, location=location)

    return render_template('check_report.html', incidents=[], city='', location={'lat': 0, 'lng': 0})

# Route to submit a report
@app.route('/submit_report', methods=['GET', 'POST'])
def submit_report():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        disaster_type = request.form['disaster_type']
        description = request.form['description']

        # Add the report to Firestore
        db.collection('emergencies').add({
            'name': name,
            'location': location,
            'disaster_type': disaster_type,
            'description': description,
            'timestamp': firestore.SERVER_TIMESTAMP
        })

        return redirect(url_for('index'))

    return render_template('submit_report.html')

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)

