import re
import time
from api.utils.avatar_generator import generate_initial_avatar

SEED_DATA_PATH = 'seed_data.sql'

def regenerate_seed_avatars():
    print("Reading seed_data.sql...")
    with open(SEED_DATA_PATH, 'r') as f:
        content = f.read()
    
    pattern = r"(\('([^']+)',.*?)('http://localhost:5000/static/uploads/[^']+')(\))"
    
    matches = re.findall(pattern, content)
    print(f"Found {len(matches)} users to update.")

    new_content = content
    
    for full_match, username, old_url_with_quotes, closing_paren in matches:
        
        print(f"Generating avatar for {username}...")
        try:
            new_url = generate_initial_avatar(username)
            new_url_sql = f"'{new_url}'"
            new_content = new_content.replace(old_url_with_quotes, new_url_sql)
            time.sleep(0.1)
        except Exception as e:
            print(f"Error for {username}: {e}")

    print("Writing updated seed_data.sql...")
    with open(SEED_DATA_PATH, 'w') as f:
        f.write(new_content)
    
    print("Done!")

if __name__ == "__main__":
    regenerate_seed_avatars()
