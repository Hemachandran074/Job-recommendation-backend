"""
Add user via API endpoint (easier than direct DB access)
"""
import requests
import json

# Backend URL
BACKEND_URL = "https://job-recommendation-backend-du8j.onrender.com/api/v1"

def add_user():
    """Add user via API"""
    print("📝 Create New User via API\n")
    
    # Get user input
    name = input("Name: ")
    email = input("Email: ")
    password = input("Password (6+ chars): ")
    
    # Validate
    if len(password) < 6:
        print("❌ Password must be at least 6 characters")
        return
    
    # Create user data
    user_data = {
        "name": name,
        "email": email,
        "password": password
    }
    
    print(f"\n🔐 Creating user: {email}")
    print("🌐 Sending request to backend...")
    
    try:
        # Call registration API
        response = requests.post(
            f"{BACKEND_URL}/users/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            user = response.json()
            print(f"\n✅ User created successfully!")
            print(f"   ID: {user.get('id')}")
            print(f"   Name: {user.get('name')}")
            print(f"   Email: {user.get('email')}")
            print(f"\n✨ You can now sign in with this account!")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    add_user()
