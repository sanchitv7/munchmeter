import aiosqlite
from app.config import settings

DATABASE_URL = settings.database_url


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DATABASE_URL)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS meal_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                meal_slot TEXT NOT NULL,
                transcription TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS meal_log_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal_log_id INTEGER NOT NULL REFERENCES meal_logs(id) ON DELETE CASCADE,
                ingredient_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                carbs REAL NOT NULL,
                fat REAL NOT NULL,
                source TEXT NOT NULL
            );
        """)
        await db.commit()
