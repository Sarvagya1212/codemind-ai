from database import engine, check_connection
from models import Base
from sqlalchemy import inspect

print("🔍 Testing connection...")
if not check_connection():
    print("❌ Cannot connect!")
    exit(1)

print("\n🗑️ Dropping existing tables...")
Base.metadata.drop_all(bind=engine)

print("🔨 Creating tables...")
Base.metadata.create_all(bind=engine)

print("\n📋 Verifying tables...")
inspector = inspect(engine)
tables = inspector.get_table_names()

if tables:
    print(f"✅ Success! Found {len(tables)} tables:")
    for t in tables:
        print(f"   - {t}")
else:
    print("❌ No tables found!")
    
print("\n🔍 Check in Docker:")
print('docker exec -it codemind_postgres psql -U codemind_user -d codemind_db -c "\\dt"')
