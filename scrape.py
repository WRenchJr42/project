import requests
from bs4 import BeautifulSoup
import re
import time

# Router details
ROUTER_URL = "http://192.168.0.1"
STATUS_PAGE = f"{ROUTER_URL}/status"
LOGIN_URL = f"{ROUTER_URL}/login.cgi"  # Change if different
PASSWORD = "your_router_password"

# Session to maintain login state
session = requests.Session()

def login():
    """Authenticate with the router."""
    data = {
        "password": PASSWORD  # Adjust field name if different
    }
    headers = {
        "Referer": ROUTER_URL  # Some routers require this
    }
    
    response = session.post(LOGIN_URL, data=data, headers=headers)
    return "logout" in response.text.lower()  # Check if login was successful

def get_public_ip():
    """Fetch the public IP from the router's status page."""
    response = session.get(STATUS_PAGE)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract IP using regex (modify if needed)
    ip_match = re.search(r'\b\d+\.\d+\.\d+\.\d+\b', soup.text)
    if ip_match:
        return ip_match.group(0)
    return None

def update_ip():
    if not login():
        print("Login failed!")
        return

    new_ip = get_public_ip()
    
    if new_ip:
        with open("last_ip.txt", "r") as file:
            old_ip = file.read().strip()
        
        if new_ip != old_ip:
            print(f"IP changed: {old_ip} → {new_ip}")
            update_your_app(new_ip)  # Modify this function
            with open("last_ip.txt", "w") as file:
                file.write(new_ip)
        else:
            print("IP has not changed.")

def update_your_app(new_ip):
    """Modify this function to update your app dynamically."""
    print(f"Updating app with new IP: {new_ip}")

if __name__ == "__main__":
    while True:
        update_ip()
        time.sleep(3600)  # Check every hour
