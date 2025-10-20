from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# EXPLICITLY set Docker PostgreSQL credentials - NO environment variables
DATABASE_URL = "postgresql://postgres:Sarvagya5678@db.afvgtdvwbunhxblsirtm.supabase.co:5432/postgres"

# Log the exact URL being used
logger.info(f"🔌 Using DATABASE_URL: {DATABASE_URL}")

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False,
    isolation_level="AUTOCOMMIT"  # Ensure DDL statements commit immediately
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """FastAPI dependency"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Create all tables"""
    try:
        # Verify connection first
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), current_user"))
            db_name, user = result.fetchone()
            logger.info(f"📡 Connected to: {db_name} as {user}")
            
            if db_name != "codemind_db":
                logger.error(f"❌ Wrong database! Expected 'codemind_db', got '{db_name}'")
                return False
        
        logger.info("🔨 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if tables:
            logger.info(f"✅ Tables created in codemind_db: {tables}")
            return True
        else:
            logger.error("❌ No tables were created!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def drop_db():
    """Drop all tables"""
    try:
        logger.info("🗑️ Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Tables dropped!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {e}")
        return False

def check_connection():
    """Test database connectivity"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_database(), current_user"))
            db_name, user = result.fetchone()
            logger.info(f"✅ Connected to database: {db_name} as {user}")
            
            if db_name != "codemind_db" or user != "codemind_user":
                logger.warning(f"⚠️ Unexpected connection: {db_name}/{user}")
                
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def get_table_info():
    """Get table information"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    info = {}
    for table in tables:
        columns = [col['name'] for col in inspector.get_columns(table)]
        info[table] = columns
    
    return info
