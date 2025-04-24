from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
import csv
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Needed for session

# Email setup
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Using google so using Gmail SMTP server (Simple Mail Transfer Protocol)
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tomtest0606@gmail.com'  # Your email here
app.config['MAIL_PASSWORD'] = 'rdtoyqqxoolahscc' # Google App Password
app.config['MAIL_DEFAULT_SENDER'] = 'tomtest0606@gmail.com'  # The email that sends the order

mail = Mail(app)

# Load parts from CSV
def load_parts():
    parts = []
    with open('parts.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            parts.append(row)
    return parts

@app.route('/')
def index():
    parts = load_parts()
    query = request.args.get('q', '').lower()
    if query:
        parts = [p for p in parts if query in p['Title'].lower() or query in p['Description'].lower()]
    return render_template('index.html', parts=parts)

@app.route('/add-to-basket', methods=['POST'])
def add_to_basket():
    part_number = request.form['part_number']
    all_parts = load_parts()
    part = next((p for p in all_parts if p['Part Number'] == part_number), None)

    if part:
        if 'basket' not in session:
            session['basket'] = []
        session['basket'].append(part)
        session.modified = True
    return redirect(url_for('index'))

@app.route('/basket')
def basket():
    basket = session.get('basket', [])
    return render_template('basket.html', basket=basket)

@app.route('/remove-from-basket', methods=['POST'])
def remove_from_basket():
    part_number = request.form['part_number']
    basket = session.get('basket', [])
    
    for i, part in enumerate(basket):
        if part['Part Number'] == part_number:
            del basket[i]
            break  # Remove only the first occurrence and exit the loop
    
    session['basket'] = basket
    session.modified = True
    return redirect(url_for('basket'))

@app.route('/send-order', methods=['POST'])
def send_order():
    name = request.form['name']
    basket = session.get('basket', [])

    # Email setup
    receiver_email = 'tomward0606@gmail.com'  # Placeholder receiver email (my personal email)

    # Prepare the email content
    email_body = f"Order from {name}:\n\n"
    for item in basket:
        title = item.get('Title', 'N/A')
        description = item.get('Description', 'N/A')
        part_number = item.get('Part Number', 'N/A')
        email_body += f"- {title} | {description} | {part_number}\n"

    # Send email
    msg = Message('Workshop Parts Order',
                  recipients=[receiver_email])
    msg.body = email_body
    try:
        mail.send(msg)
        # Clear basket after sending order
        session['basket'] = []
        return f"Order sent successfully by {name}!"
    except Exception as e:
        return f"Error sending email: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
