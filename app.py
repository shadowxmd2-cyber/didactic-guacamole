from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'Gx7@pL92#kT!'

API_KEY = 'a893ab9c6efabc870d271e0f2c19016b'
TELEGRAM_BOT_TOKEN = '8266023841:AAF7WQf-CngjP6KVcBJS7AeJ8WdcSYxlA5I'
TELEGRAM_CHAT_ID = '1720283336'

# In-memory user storage (for demo)
users = {}

# Home / Weather Page
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    weather_data = None
    rain_forecast = None
    city = None

    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            # Get weather
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            weather_data = requests.get(url).json()

            # Get 5-day forecast
            if 'coord' in weather_data:
                lat = weather_data['coord']['lat']
                lon = weather_data['coord']['lon']
                forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
                forecast_data = requests.get(forecast_url).json()
                rain_forecast = next((f for f in forecast_data['list'] if 'rain' in f), None)

            # Send Telegram message
            msg = f"User {session['username']} checked weather for {city}"
            requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={msg}")

    return render_template('index.html', weather=weather_data, rain=rain_forecast, city=city)

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users:
            return "User already exists"
        users[username] = password
        return redirect(url_for('login'))
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if users.get(username) == password:
            session['username'] = username
            return redirect(url_for('index'))
        return "Invalid credentials"
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
