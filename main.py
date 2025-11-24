from datetime import datetime, timedelta
from typing import Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

from sqlalchemy.orm import Session
from database import SessionLocal
from models import UserDB

app = FastAPI()

# =========================
# הגדרות בסיסיות של JWT
# =========================

SECRET_KEY = "CHANGE_THIS_TO_SOMETHING_RANDOM_AND_SECRET"  # להחליף בפרודקשן
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# סיסמה סודית לרישום מנהל (admin)
ADMIN_SECRET = "SUPER_ADMIN_SECRET"


# =========================
# "מאגר" המערך בזיכרון
# =========================

array_storage: list = ["first", "second", "third"]


# =========================
# מודלי נתונים (Pydantic models)
# =========================

class LoginRequest(BaseModel):
    """
    *כבר לא בשימוש בפועל* (השארנו כדי שתראה איך נראה JSON ל-login).
    הלוגין בפועל עובד עם form-data דרך OAuth2PasswordRequestForm.
    """
    username: str
    password: str


class TokenResponse(BaseModel):
    """מבנה תגובת ה-login: access_token (JWT) + token_type ('bearer')."""
    access_token: str
    token_type: str


class User(BaseModel):
    """
    מודל פנימי שמייצג משתמש מחובר במערכת.
    נבנה מתוך ה-JWT (sub + is_admin).
    """
    username: str
    is_admin: bool


class ArrayItem(BaseModel):
    """
    מבנה ה-JSON שנקבל בפעולות POST/PUT על המערך:
    {
        "value": ...
    }
    """
    value: Any


class RegisterRequest(BaseModel):
    """
    גוף בקשה לרישום משתמש חדש.
    - username: שם המשתמש החדש
    - password: הסיסמה הרגילה שלו
    - admin_secret: אופציונלי. אם שווה לסיסמה הסודית, המשתמש נרשם כמנהל.
    """
    username: str
    password: str
    admin_secret: str | None = None

class UserInfo(BaseModel):
    username: str
    is_admin: bool
    # במידה ועמודת created_at לא קיימת במודל ה-ORM, נשאיר כשדה אופציונלי כדי שלא ייזרק שגיאה
    created_at: datetime | None = None

    class Config:
        orm_mode = True




# =========================
# יצירת Session למסד הנתונים לכל בקשה
# =========================

def get_db():
    """
    כל Endpoint שצריך DB יקבל פרמטר:
        db: Session = Depends(get_db)

    כאן אנחנו:
    - פותחים Session למסד הנתונים
    - מחזירים אותו ל-Endpoint (yield)
    - סוגרים אותו בסיום הבקשה
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# סכמת OAuth2 – איך מוציאים את ה-token מה-Header
# =========================

# FastAPI מבין שהטוקן יגיע ב-Header:
#   Authorization: Bearer <token>
# ושה-Endpoint שמנפיק טוקן חדש הוא /login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# =========================
# פונקציה ליצירת JWT חדש
# =========================

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    יוצרת JWT חתום מהנתונים שנגדיר.
    data - מילון עם מידע על המשתמש (claims)
    expires_delta - תוך כמה זמן הטוקן יפוג
    """
    to_encode = data.copy()

    if expires_delta is not None:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    # exp - זמן תפוגה
    to_encode.update({"exp": expire})

    # יצירת ה-JWT החתום
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# =========================
# פונקציות עזר לעבודה עם משתמשים
# =========================

def get_user_by_username(db: Session, username: str) -> UserDB | None:
    """
    מחפש משתמש בטבלת users לפי username.
    אם קיים – מחזיר UserDB, אם לא – מחזיר None.
    """
    return db.query(UserDB).filter(UserDB.username == username).first()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    מקבלת JWT מה-Header, מאמתת אותו (חתימה + exp),
    שולפת את המשתמש מה-DB,
    ומחזירה אובייקט User.
    אם משהו לא תקין – זורקת 401.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # פענוח הטוקן: בדיקת חתימה + exp
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        is_admin: bool | None = payload.get("is_admin")

        if username is None or is_admin is None:
            raise credentials_exception

    except JWTError:
        # טוקן לא תקין / פג תוקף / חתימה לא תואמת
        raise credentials_exception

    # בדיקה שהמשתמש עדיין קיים ב-DB
    db_user = get_user_by_username(db, username)
    if db_user is None:
        raise credentials_exception

    return User(username=db_user.username, is_admin=db_user.is_admin)


def ensure_admin(current_user: User):
    """
    מוודאת שלמשתמש יש הרשאת מנהלן.
    אם לא – זורקת 403 (Forbidden).
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required",
        )


# =========================
# Endpoint: התחברות (LOGIN)
# =========================

@app.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    לוגין לפי תקן OAuth2 password flow:
    Swagger שולח form-data עם username + password.
    אם הפרטים נכונים - מייצר JWT ומחזיר ללקוח.
    אם לא - מחזיר 401 (Invalid username or password).
    """
    # 1. מחפשים משתמש ב-DB לפי username
    db_user = get_user_by_username(db, form_data.username)
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # 2. בודקים סיסמה (כרגע טקסט רגיל – בלי hashing, כמו במטלה)
    if form_data.password != db_user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # 3. נתונים שיוכנסו לתוך ה-JWT (payload)
    token_data = {
        "sub": db_user.username,      # subject: שם המשתמש
        "is_admin": db_user.is_admin  # האם המשתמש אדמין
    }

    # 4. זמן תפוגה
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # 5. יצירת JWT
    token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires,
    )

    # 6. החזרת הטוקן ללקוח
    return TokenResponse(access_token=token, token_type="bearer")


# =========================
# Endpoint: רישום משתמש חדש (REGISTER)
# =========================

@app.post("/users", status_code=201, response_model=User)
def register_user(
    register_data: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    רישום משתמש חדש במערכת.

    - אם username כבר קיים → מחזירים 400.
    - אם admin_secret נכון → המשתמש יירשם כמנהלן (is_admin=True).
    - אחרת → נרשום כמשתמש רגיל (is_admin=False).
    """
    # 1. לבדוק אם המשתמש כבר קיים
    existing_user = get_user_by_username(db, register_data.username)
    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail="Username already exists",
        )

    # 2. קביעת האם המשתמש יהיה מנהל
    is_admin = False
    if register_data.admin_secret not in (None, ""):
        if register_data.admin_secret == ADMIN_SECRET:
            is_admin = True
        else:
            # ניסיון להירשם כמנהלן עם סיסמה סודית שגויה → 403
            raise HTTPException(
                status_code=403,
                detail="Invalid admin secret",
            )

    # 3. יצירת אובייקט UserDB חדש
    new_user = UserDB(
        username=register_data.username,
        password=register_data.password,  # כרגע בלי hashing – לפי המטלה
        is_admin=is_admin,
    )

    # 4. שמירה ב-DB
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 5. נחזיר אובייקט User (בלי סיסמה כמובן)
    return User(username=new_user.username, is_admin=new_user.is_admin)


# =========================
# Endpoint: קידום משתמש למנהלן (PROMOTE)
# =========================

@app.put("/users/{username}/promote", response_model=User)
def promote_user_to_admin(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    קידום משתמש קיים למנהלן (admin).

    תנאים:
    - רק מנהלן מחובר יכול לקרוא ל-Endpoint הזה.
    - אם המשתמש לא קיים → מחזירים 404.
    - אם המשתמש כבר מנהלן → מחזירים 400.
    - אחרת → נהפוך אותו ל-is_admin=True ונשמור ב-DB.
    """
    # 1. לוודא שהקורא הוא מנהלן
    ensure_admin(current_user)

    # 2. לחפש את המשתמש שאותו רוצים לקדם
    target_user = get_user_by_username(db, username)
    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # 3. אם הוא כבר מנהלן – אין מה לקדם
    if target_user.is_admin:
        raise HTTPException(
            status_code=400,
            detail="User is already an admin",
        )

    # 4. קידום: להפוך את המשתמש למנהלן
    target_user.is_admin = True
    db.commit()
    db.refresh(target_user)

    # 5. מחזירים אובייקט User (בלי סיסמה כמובן)
    return User(username=target_user.username, is_admin=target_user.is_admin)


# =========================
# Endpoint: הורדת משתמש מדרגת מנהלן (DEMOTE) — סעיף 3
# =========================

@app.put("/users/{username}/demote", response_model=User)
def demote_user_to_regular(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    הורדת משתמש מדרגת Admin למשתמש רגיל.

    תנאים:
    - רק מנהלן מחובר יכול לקרוא ל-Endpoint הזה.
    - אם המשתמש לא קיים → מחזירים 404.
    - אם המשתמש כבר רגיל → מחזירים 400.
    - אחרת → נהפוך אותו ל-is_admin=False ונשמור ב-DB.
    """
    # 1. לוודא שהקורא הוא מנהלן
    ensure_admin(current_user)

    # 2. לחפש את המשתמש שאותו רוצים להוריד
    target_user = get_user_by_username(db, username)
    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # 3. אם הוא כבר רגיל – אין מה להוריד
    if not target_user.is_admin:
        raise HTTPException(
            status_code=400,
            detail="User is already regular",
        )

    # 4. הורדה: להפוך את המשתמש לרגיל
    target_user.is_admin = False
    db.commit()
    db.refresh(target_user)

    # 5. מחזירים אובייקט User (בלי סיסמה כמובן)
    return User(username=target_user.username, is_admin=target_user.is_admin)


# ======================================================
# מכאן ואילך – כל ה-Endpoints (חוץ מ-/login ו-/users) דורשים JWT
# ======================================================

@app.get("/")
def read_root(current_user: User = Depends(get_current_user)):
    """
    דף ברירת מחדל.
    דורש משתמש מחובר.
    מחזיר:
    "Hello <username> today is <current date>"
    תחת השדה msg (לפי הדרישה).
    """
    today_str = datetime.utcnow().date().isoformat()
    return {"msg": f"Hello {current_user.username} today is {today_str}"}


@app.get("/health")
def health_check(current_user: User = Depends(get_current_user)):
    """
    בדיקת תקינות השרת – גם היא מוגנת ב-JWT (לפי הדרישה).
    """
    return {"status": "ok"}


@app.get("/echo")
def echo_message(
    msg: str,
    current_user: User = Depends(get_current_user)
):
    """
    מקבל Query string בשם msg,
    ומחזיר ללקוח את ההודעה חזרה.
    דורש JWT תקין.
    """
    return {"echo": f"The message is {msg}", "user": current_user.username}


@app.get("/array")
def get_array(current_user: User = Depends(get_current_user)):
    """
    מחזיר את המערך כולו.
    דורש JWT.
    (אין צורך בהרשאת אדמין – רק קריאה.)
    """
    return {"array": array_storage}


@app.get("/array/{index}")
def get_array_value(
    index: int,
    current_user: User = Depends(get_current_user)
):
    """
    מחזיר את הערך באינדקס מסוים במערך.
    אם האינדקס מחוץ לטווח - מחזיר 404.
    דורש JWT.
    """
    if index < 0 or index >= len(array_storage):
        raise HTTPException(status_code=404, detail="Index out of range")

    value = array_storage[index]
    return {"value": value}

@app.get("/users", response_model=list[UserInfo])
def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    מחזיר רשימה של כל המשתמשים במערכת.
    דורש משתמש עם הרשאת Admin.
    """
    ensure_admin(current_user)

    users = db.query(UserDB).all()
    return users




@app.post("/array", status_code=201)
def add_to_array(
    item: ArrayItem,
    current_user: User = Depends(get_current_user)
):
    """
    מוסיף ערך חדש לסוף המערך.
    מקבל JSON בגוף הבקשה {"value": ...}
    מחזיר 201 (Created).
    דורש JWT **והרשאת אדמין**.
    """
    ensure_admin(current_user)

    array_storage.append(item.value)
    return {"array": array_storage}


@app.put("/array/{index}")
def update_array_value(
    index: int,
    item: ArrayItem,
    current_user: User = Depends(get_current_user)
):
    """
    מעדכן ערך קיים באינדקס מסוים.
    אם האינדקס מחוץ לטווח - 404.
    דורש JWT **והרשאת אדמין**.
    """
    ensure_admin(current_user)

    if index < 0 or index >= len(array_storage):
        raise HTTPException(status_code=404, detail="Index out of range")

    array_storage[index] = item.value
    return {"index": index, "value": item.value}


@app.delete("/array")
def delete_last_value(current_user: User = Depends(get_current_user)):
    """
    מוחק את הערך האחרון במערך.
    אם המערך ריק - מחזירים 400 (אין מה למחוק).
    דורש JWT **והרשאת אדמין**.
    """
    ensure_admin(current_user)

    if not array_storage:
        raise HTTPException(status_code=400, detail="Array is empty")

    deleted_value = array_storage.pop()
    return {"deleted": deleted_value, "array": array_storage}


@app.delete("/array/{index}")
def delete_by_index(
    index: int,
    current_user: User = Depends(get_current_user)
):
    """
    "מאפס" את הערך באינדקס מסוים ל-0 (לפי דרישות המטלה).
    אם האינדקס מחוץ לטווח - 404.
    דורש JWT **והרשאת אדמין**.
    """
    ensure_admin(current_user)

    if index < 0 or index >= len(array_storage):
        raise HTTPException(status_code=404, detail="Index out of range")

    array_storage[index] = 0
    return {"index": index, "array": array_storage}
