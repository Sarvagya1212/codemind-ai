"""
Database initialization script
Run this to create all tables in Docker PostgreSQL
"""
import sys
from database import check_connection, init_db, engine
from sqlalchemy import inspect

def main():
    print("=" * 60)
    print("CodeMind AI - Database Initialization")
    print("=" * 60)
    
    # Check connection
    print("\n Testing database connection...")
    if not check_connection():
        print(" Cannot connect to database.")
        print("   Check: docker-compose ps")
        sys.exit(1)
    
    # Check existing tables
    print("\n Checking existing tables...")
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if existing_tables:
        print(f"  Found existing tables: {existing_tables}")
        response = input("   Drop and recreate? (yes/no): ")
        if response.lower() == 'yes':
            from models import Base
            Base.metadata.drop_all(bind=engine)
            print(" Tables dropped")
    else:
        print("   No existing tables found")
    
    # Create tables
    print("\n Creating tables...")
    if not init_db():
        print(" Failed to create tables")
        sys.exit(1)
    
    # Verify creation
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n Successfully created {len(tables)} tables:")
    for table in tables:
        columns = inspector.get_columns(table)
        indexes = inspector.get_indexes(table)
        print(f"    {table}")
        print(f"      - Columns: {len(columns)}")
        print(f"      - Indexes: {len(indexes)}")
    
    print("\n" + "=" * 60)
    print(" Database initialization complete!")
    print("=" * 60)
    print("\nVerify with:")
    print('   docker exec -it codemind_postgres psql -U codemind_user -d codemind_db -c "\\dt"')
    print()

if __name__ == "__main__":
    main()
