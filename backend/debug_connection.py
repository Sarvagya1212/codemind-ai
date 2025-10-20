

from sqlalchemy import create_engine, inspect, text
import sys

# EXACT same URL as database.py
docker_url = "postgresql://postgres:Sarvagya5678@db.afvgtdvwbunhxblsirtm.supabase.co:5432/postgres"

print("=" * 60)
print("DATABASE CONNECTION DIAGNOSTIC")
print("=" * 60)
print(f"\n🔍 Testing: {docker_url}\n")

try:
    engine = create_engine(docker_url, echo=False)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database(), current_user"))
        db_name, user = result.fetchone()
        print(f"✅ Connected successfully!")
        print(f"   Database: {db_name}")
        print(f"   User: {user}")
        
        if db_name != "codemind_db":
            print(f"\n⚠️  WARNING: Connected to wrong database!")
            print(f"   Expected: codemind_db")
            print(f"   Got: {db_name}")
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📋 Tables in {db_name}: {len(tables)}")
        if tables:
            for table in tables:
                print(f"   - {table}")
        else:
            print("   (No tables)")
            
except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
