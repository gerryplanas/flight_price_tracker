import requests
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
API_KEY = 'YOUR_RAPIDAPI_KEY'
EMAIL_SENDER = 'your_email@example.com'
EMAIL_RECEIVER = 'receiver_email@example.com'
EMAIL_PASSWORD = 'your_email_password'  # Use App Password if using Gmail
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
PRICE_THRESHOLD = 150  # Set your target price

# Flight check function
def find_cheapest_flight_and_alert():
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': 'skyscanner-skyscanner-flight-search-v1.p.rapidapi.com'
    }

    origin = 'SFO'
    destination = 'AUS'
    today = datetime.date.today()
    outbound_date = today.strftime('%Y-%m-%d')

    url = f"https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/US/USD/en-US/{origin}/{destination}/{outbound_date}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        quotes = data.get('Quotes', [])
        if quotes:
            cheapest = min(quotes, key=lambda x: x['MinPrice'])
            price = cheapest['MinPrice']
            carrier_id = cheapest['OutboundLeg']['CarrierIds'][0]
            carrier = next((c['Name'] for c in data['Carriers'] if c['CarrierId'] == carrier_id), 'Unknown')

            if price <= PRICE_THRESHOLD:
                send_email_alert(origin, destination, outbound_date, price, carrier)
            else:
                print(f"No deals found under ${PRICE_THRESHOLD}. Cheapest: ${price}")
        else:
            print("No flights found.")
    else:
        print(f"API Error: {response.status_code}")

# Email alert function
def send_email_alert(origin, destination, date, price, carrier):
    subject = f"🔥 Cheap Flight Found: ${price} from {origin} to {destination}"
    body = (
        f"Good news!\n\n"
        f"We found a flight from {origin} to {destination} on {date} for just ${price}.\n"
        f"Airline: {carrier}\n\n"
        f"Check it out on Skyscanner or your preferred booking site."
    )

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        print("✈️ Email alert sent!")

# Run script
find_cheapest_flight_and_alert()