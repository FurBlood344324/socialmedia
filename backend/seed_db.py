import os
import sys
from sqlalchemy import create_engine

# Add current directory to path so we can import api
sys.path.append(os.getcwd())

from api.config import Config

def seed_db():
    print("Seeding database...")
    
    # Get URI from Config
    uri = Config.SQLALCHEMY_DATABASE_URI
    
    try:
        engine = create_engine(uri)
        # Use raw connection for executing SQL script with multiple statements
        raw_conn = engine.raw_connection()
        cursor = raw_conn.cursor()
        
        try:
            # 1. Truncate tables
            print("Truncating tables...")
            # We use CASCADE to handle foreign key dependencies
            # Order doesn't strictly matter with CASCADE, but good to be thorough
            tables = [
                "Users", "Communities", "Roles", "PrivacyTypes", "FollowStatus",
                "Posts", "Comments", "PostLikes", "CommunityMembers", 
                "Follows", "Messages"
            ]
            
            for table in tables:
                # Check if table exists before truncating to avoid errors if init.sql wasn't run
                # But typically we assume schema exists. 
                # To be safe against "relation does not exist" if schema is empty, we could wrap in try/except 
                # but valid schema is a prerequisite for seeding.
                try:
                    cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
                except Exception as table_e:
                    # If table doesn't exist, just skip it but warn? 
                    # Actually, if tables don't exist, we can't seed anyway.
                    # Let's assume schema exists as per requirement.
                    pass

            # 2. Read seed_data.sql
            print("Reading seed_data.sql...")
            with open('seed_data.sql', 'r') as f:
                sql_content = f.read()
                
            # 3. Execute SQL content
            print("Executing seed statements...")
            cursor.execute(sql_content)
            
            raw_conn.commit()
            print("Database seeding successful!")
            
        except Exception as e:
            raw_conn.rollback()
            print(f"Error executing SQL: {e}")
            sys.exit(1)
        finally:
            cursor.close()
            raw_conn.close()
            
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    seed_db()
