# backend-project/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. כתובת החיבור למסד הנתונים (PostgreSQL)
# הפרוטוקול  -> "postgresql"
# המשתמש     -> "postgres"
# הסיסמה     -> "admin"      (כמו שקבעת בזמן ההתקנה)
# השרת       -> "localhost"
# הפורט      -> "5432"
# שם מסד הנתונים -> "node_exercise"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@localhost:5432/node_exercise"

# 2. יצירת engine – אובייקט שמנהל את החיבור ל-DB
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
# echo=True רק כדי לראות לוגים של ה-SQL במסך

# 3. SessionLocal – "מפעל" ליצירת אובייקטים של Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base – ממנו כל המודלים (הטבלאות) יורשים
Base = declarative_base()

# אופציונלי בלבד: אם תריץ ישירות את הקובץ הזה,
# הוא ייצור את הטבלאות ב-DB לפי המודלים.
if __name__ == "__main__":
    from models import UserDB  # שים לב: בלי נקודה לפני models

    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")
