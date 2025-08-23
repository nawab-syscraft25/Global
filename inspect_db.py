import asyncio
import asyncpg
from sqlalchemy import create_engine, text, inspect
from app.config import settings

async def inspect_database():
    """Inspect current database structure"""
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    print("Current Database Structure:")
    print("=" * 50)
    
    for table_name in inspector.get_table_names():
        print(f"\nTable: {table_name}")
        print("-" * 30)
        
        columns = inspector.get_columns(table_name)
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f" DEFAULT {col['default']}" if col['default'] else ""
            print(f"  {col['name']}: {col['type']} {nullable}{default}")
        
        # Get primary keys
        pk = inspector.get_pk_constraint(table_name)
        if pk['constrained_columns']:
            print(f"  PRIMARY KEY: {', '.join(pk['constrained_columns'])}")
        
        # Get foreign keys
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            print(f"  FOREIGN KEY: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        # Get indexes
        indexes = inspector.get_indexes(table_name)
        for idx in indexes:
            print(f"  INDEX: {idx['name']} on {idx['column_names']}")

if __name__ == "__main__":
    asyncio.run(inspect_database())
