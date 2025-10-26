"""
Admin endpoints for database management
"""
import logging
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.database import get_engine

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/migrate")
async def run_migration():
    """
    Run database migrations to add missing columns
    
    This endpoint should be called once after deployment to ensure
    all required columns exist in the database.
    """
    try:
        logger.info("🔄 Starting database migration via API...")
        
        engine = get_engine()
        
        async with engine.begin() as conn:
            # Enable pgvector extension
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                logger.info("✅ pgvector extension enabled")
            except Exception as e:
                logger.warning(f"⚠️ pgvector: {e}")
            
            # Add missing columns to users table
            migrations = [
                # Basic profile columns
                """
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS location VARCHAR(255),
                ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
                ADD COLUMN IF NOT EXISTS bio TEXT,
                ADD COLUMN IF NOT EXISTS linkedin VARCHAR(255),
                ADD COLUMN IF NOT EXISTS github VARCHAR(255),
                ADD COLUMN IF NOT EXISTS portfolio VARCHAR(255)
                """,
                
                # Account status columns
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
                ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT false,
                ADD COLUMN IF NOT EXISTS last_login TIMESTAMP
                """,
                
                # Personalization columns (the missing ones!)
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS preferred_job_titles JSON DEFAULT '[]'::json,
                ADD COLUMN IF NOT EXISTS experience_level VARCHAR(50) DEFAULT 'Entry Level',
                ADD COLUMN IF NOT EXISTS preferred_locations JSON DEFAULT '[]'::json,
                ADD COLUMN IF NOT EXISTS experience_years INTEGER,
                ADD COLUMN IF NOT EXISTS preferred_job_type VARCHAR(50),
                ADD COLUMN IF NOT EXISTS resume_text TEXT,
                ADD COLUMN IF NOT EXISTS resume_embedding vector(384)
                """,
            ]
            
            results = []
            for i, migration in enumerate(migrations, 1):
                try:
                    await conn.execute(text(migration))
                    logger.info(f"✅ Migration {i} applied successfully")
                    results.append(f"Migration {i}: SUCCESS")
                except Exception as e:
                    logger.error(f"❌ Migration {i} failed: {e}")
                    results.append(f"Migration {i}: FAILED - {str(e)}")
            
            # Create indexes
            try:
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                    CREATE INDEX IF NOT EXISTS idx_users_location ON users(location);
                    CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);
                    CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
                    CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);
                """))
                logger.info("✅ Indexes created")
                results.append("Indexes: SUCCESS")
            except Exception as e:
                logger.warning(f"⚠️ Index creation: {e}")
                results.append(f"Indexes: WARNING - {str(e)}")
            
            await conn.commit()
        
        logger.info("🎉 Database migration completed!")
        
        return {
            "status": "success",
            "message": "Database migration completed successfully",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Migration failed: {str(e)}"
        )


@router.get("/check-columns")
async def check_columns():
    """
    Check which columns exist in the users table
    """
    try:
        engine = get_engine()
        
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """))
            
            columns = []
            for row in result:
                columns.append({
                    "name": row[0],
                    "type": row[1],
                    "nullable": row[2]
                })
            
            return {
                "status": "success",
                "table": "users",
                "total_columns": len(columns),
                "columns": columns
            }
            
    except Exception as e:
        logger.error(f"Error checking columns: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check columns: {str(e)}"
        )
