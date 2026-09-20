from mem0 import MemoryClient
from dotenv import load_dotenv
import requests
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

memClient = MemoryClient(api_key=os.getenv("MEM0_API"))

def get_weather(location: str):

    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_response = requests.get(
            geo_url,
            params={"name": location, "count": 1, "language": "en", "format": "json"},
        )

        geo_data = geo_response.json()

        if "results" not in geo_data:
            return {"error": f"Could not find location: {location}"}

        place = geo_data["results"][0]

        latitude = place["latitude"]
        longitude = place["longitude"]

        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_response = requests.get(
            weather_url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            },
        )

        weather_data = weather_response.json()

        return {
            "location": location,
            "temperature": weather_data["current"]["temperature_2m"],
            "humidity": weather_data["current"]["relative_humidity_2m"],
            "wind_speed": weather_data["current"]["wind_speed_10m"],
            "weather_code": weather_data["current"]["weather_code"],
        }
    except Exception as e:
        print(f"Weather info exception -> {e}")


def save_to_file(filename: str, content: str):

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)

        return {"success": True, "message": f"Data saved to {filename}"}
    except Exception as e:
        print(f"File saving exception -> {e}")


def get_memories():
    try:
        USER_ID = "sudipto"
        memories = memClient.get_all(filters={"user_id": "sudipto"})

        return memories
    except Exception as e:
        print(f"Memory fetching exception -> {e}")


def send_mail(to: str, subject: str, content: str):
    smtp_server = os.getenv("SMTP_SERVER")
    port = os.getenv("SMTP_PORT")
    sender_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    try:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = to
        message['Subject'] = subject

        body = content
        message.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(message)
        server.quit()

        return {
            "success": True,
            "message": f"Email successfully sent to {to}"
        }
    except Exception as e:
        print(f"Mail sending exception -> {e}")


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather of a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City or location name",
                    }
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_to_file",
            "description": "Save text content into a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the file"},
                    "content": {"type": "string", "description": "Content to save"},
                },
                "required": ["filename", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_mail",
            "description": "Send mail to a email address",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "destination email address"},
                    "content": {"type": "string", "description": "The actual body that should be written on the email"},
                    "subject": {"type": "string", "description": "The subject line of the email"},
                },
                "required": ["to", "content", "subject"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_memories",
            "description": "Get stored memories for a user from Mem0.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

tool_functions = {
    "get_weather": get_weather,
    "save_to_file": save_to_file,
    "get_memories": get_memories,
    "send_mail": send_mail
}
