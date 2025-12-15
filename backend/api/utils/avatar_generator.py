import os
import random
import time

BASE_URL = 'http://localhost:5000/static/uploads'

def generate_initial_avatar(username):
    """Generates a default SVG avatar locally to avoid network dependency."""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    upload_path = os.path.join(backend_dir, 'static', 'uploads')
    
    os.makedirs(upload_path, exist_ok=True)
    
    # Generate random dark color for contrast with white text
    r = random.randint(50, 200)
    g = random.randint(50, 200)
    b = random.randint(50, 200)
    color = f"rgb({r},{g},{b})"
    
    initials = username[:2].upper() if len(username) > 1 else username[:1].upper()
    
    svg_content = f'''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="{color}"/>
  <text x="50%" y="54%" font-family="Arial, sans-serif" font-weight="bold" font-size="80" fill="white" dominant-baseline="middle" text-anchor="middle">
    {initials}
  </text>
</svg>'''
    
    filename = f"{username}_{int(time.time())}_default.svg"
    file_full_path = os.path.join(upload_path, filename)
    
    with open(file_full_path, 'w') as f:
        f.write(svg_content)
        
    return f"{BASE_URL}/{filename}"
