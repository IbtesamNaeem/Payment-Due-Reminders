import json
from datetime import datetime, timedelta
from twilio.rest import Client
import os
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta

# Load environment variables
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
MY_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")  # Updated to match the .env file

# Initialize Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Load payment data
def load_payments():
    with open("payments.json", "r") as f:
        return json.load(f)

# Save updated payment data
def save_payments(payments):
    with open("payments.json", "w") as f:
        json.dump(payments, f, indent=4)

# Send reminder
def send_reminder(payment_name, due_date):
    message = f"Reminder: Your {payment_name} is due on {due_date}. Please make the payment in time!"
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=MY_PHONE_NUMBER
    )
    print(f"Sent reminder for {payment_name} (Due: {due_date})")

# Calculate next due date based on recurrence
def calculate_next_due_date(due_date, recurrence):
    if recurrence == "monthly":
        due_date = datetime.strptime(due_date, "%Y-%m-%d")
        next_due_date = due_date + relativedelta(months=1)  # Add 1 month accurately
        return next_due_date.strftime("%Y-%m-%d")
    return None

# Check for upcoming payments and update recurring payments
def check_due_payments():
    today = datetime.now().date()
    upcoming_date = today + timedelta(days=3)

    payments = load_payments()
    updated_payments = []

    for payment in payments:
        due_date = datetime.strptime(payment["due_date"], "%Y-%m-%d").date()
        if due_date == upcoming_date:
            send_reminder(payment["name"], payment["due_date"])

        # Update due date for recurring payments
        if "recurrence" in payment and payment["recurrence"] == "monthly":
            if due_date <= today:  # Payment date has passed, update to next recurrence
                payment["due_date"] = calculate_next_due_date(payment["due_date"], payment["recurrence"])

        updated_payments.append(payment)

    # Save updated payments back to the file
    save_payments(updated_payments)

print(f"TWILIO_ACCOUNT_SID: {TWILIO_ACCOUNT_SID}")
print(f"TWILIO_AUTH_TOKEN: {TWILIO_AUTH_TOKEN}")
print(f"TWILIO_PHONE_NUMBER: {TWILIO_PHONE_NUMBER}")
print(f"MY_PHONE_NUMBER: {MY_PHONE_NUMBER}")

if __name__ == "__main__":
    check_due_payments()
