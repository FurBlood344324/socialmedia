import os
import requests
import time

BASE_URL = 'http://localhost:5000/static/uploads'

def generate_initial_avatar(username):
    """Generates a default avatar using ui-avatars.com and saves it locally."""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    upload_path = os.path.join(backend_dir, 'static', 'uploads')
    
    os.makedirs(upload_path, exist_ok=True)
    api_url = f"https://ui-avatars.com/api/?name={username}&background=random&color=000&size=200&font-size=0.5&length=2&bold=true"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        filename = f"{username}_{int(time.time())}_default.png"
        file_full_path = os.path.join(upload_path, filename)
        
        with open(file_full_path, 'wb') as f:
            f.write(response.content)
            
        return f"{BASE_URL}/{filename}"
        
    except Exception as e:
        print(f"Error fetching avatar from ui-avatars.com: {e}")
        return f"{BASE_URL}/default_placeholder.png"
