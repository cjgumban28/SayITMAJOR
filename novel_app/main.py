from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import bcrypt
import jwt
from typing import Optional
import logging

SECRET_KEY = "my_secret_key"

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)

# Database connection helper for SQLite
def get_db():
    db = sqlite3.connect("novel_db.db")
    db.row_factory = sqlite3.Row  # This allows us to access columns by name
    return db

def create_user_token(user_id: int):
    # PyJWT: encode method should be available
    token = jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm="HS256")
    return token

# Verify JWT token
def verify_token(token: Optional[str]):
    if token is None:
        raise HTTPException(status_code=401, detail="Token is required")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Models
class UserCreate(BaseModel):
    username: str
    password: str
    email: str

class UserLogin(BaseModel):
    username: str
    password: str

class NovelCreate(BaseModel):
    title: str
    description: str
    content: str

class LikeCreate(BaseModel):
    novel_id: int

class CommentCreate(BaseModel):
    novel_id: int
    text: str

class WishListCreate(BaseModel):
    novel_id: int

class ProfileUpdate(BaseModel):
    username: str
    email: str
    password: str

# Database table creation on startup
def create_tables():
    db = get_db()
    cursor = db.cursor()

    # Create the 'users' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Create the 'novels' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS novels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            content TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Create the 'likes' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            novel_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY (novel_id) REFERENCES novels(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Create the 'comments' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            novel_id INTEGER,
            user_id INTEGER,
            text TEXT,
            FOREIGN KEY (novel_id) REFERENCES novels(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Create the 'wishlists' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            novel_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY (novel_id) REFERENCES novels(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    db.commit()
    db.close()

@app.on_event("startup")
def on_startup():
    create_tables()

# User registration endpoint
@app.post("/users/")
def create_user(user: UserCreate):
    db = get_db()
    cursor = db.cursor()

    # Hash password before storing it
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                   (user.username, user.email, hashed_password))
    db.commit()
    db.close()

    return {"msg": "User created successfully"}

@app.post("/login/")
def login_user(user: UserLogin):
    db = None
    try:
        # Establish DB connection
        db = get_db()
        cursor = db.cursor()

        # Query user by username
        cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
        db_user = cursor.fetchone()

        # Check if the user exists
        if not db_user:
            raise HTTPException(status_code=400, detail="Invalid username")

        # Verify the password by comparing the hashed password in the database
        if not bcrypt.checkpw(user.password.encode('utf-8'), db_user['password']):
            raise HTTPException(status_code=400, detail="Invalid password")

        # Generate token
        token = create_user_token(db_user['id'])
        return {"token": token}

    except sqlite3.Error as db_err:
        logging.error(f"Database error: {db_err}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(db_err)}")
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    finally:
        # Safely close the database connection
        if db:
            db.close()

@app.post("/novels/")
def upload_novel(novel: NovelCreate, token: Optional[str] = None):
    user_id = verify_token(token)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("INSERT INTO novels (title, description, content, user_id) VALUES (?, ?, ?, ?)", 
                   (novel.title, novel.description, novel.content, user_id))
    db.commit()
    db.close()

    return {"msg": "Novel uploaded successfully"}

@app.post("/novels/like/")
def like_novel(like: LikeCreate, token: Optional[str] = None):
    user_id = verify_token(token)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("INSERT INTO likes (novel_id, user_id) VALUES (?, ?)", 
                   (like.novel_id, user_id))
    db.commit()
    db.close()

    return {"msg": "Liked the novel"}

@app.post("/novels/comment/")
def comment_novel(comment: CommentCreate, token: Optional[str] = None):
    user_id = verify_token(token)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("INSERT INTO comments (novel_id, user_id, text) VALUES (?, ?, ?)", 
                   (comment.novel_id, user_id, comment.text))
    db.commit()
    db.close()

    return {"msg": "Comment added"}

@app.post("/wishlist/")
def add_to_wishlist(wishlist: WishListCreate, token: Optional[str] = None):
    user_id = verify_token(token)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("INSERT INTO wishlists (novel_id, user_id) VALUES (?, ?)", 
                   (wishlist.novel_id, user_id))
    db.commit()
    db.close()

    return {"msg": "Added to wishlist"}

@app.get("/novels/{novel_id}/download/")
def download_novel(novel_id: int):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM novels WHERE id = ?", (novel_id,))
    novel = cursor.fetchone()
    db.close()

    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")

    return novel

@app.put("/novels/{novel_id}/")
def update_novel(novel_id: int, novel: NovelCreate, token: Optional[str] = None):
    user_id = verify_token(token)

    db = get_db()
    cursor = db.cursor()

    # Update the novel's title, description, and content if the user owns the novel
    query = "UPDATE novels SET title = ?, description = ?, content = ? WHERE id = ? AND user_id = ?"
    cursor.execute(query, (novel.title, novel.description, novel.content, novel_id, user_id))
    db.commit()
    db.close()

    return {"msg": "Novel updated successfully"}

@app.delete("/novels/{novel_id}/")
def delete_novel(novel_id: int, token: Optional[str] = None):
    user_id = verify_token(token)

    db = get_db()
    cursor = db.cursor()

    # Delete the novel only if the user is the one who uploaded it
    cursor.execute("DELETE FROM novels WHERE id = ? AND user_id = ?", (novel_id, user_id))
    db.commit()
    db.close()

    return {"msg": "Novel deleted successfully"}

@app.get("/users/{user_id}/novels/")
def get_user_novels(user_id: int):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM novels WHERE user_id = ?", (user_id,))
    novels = cursor.fetchall()
    db.close()

    return novels

@app.get("/novels/")
def get_all_novels():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM novels")
    novels = cursor.fetchall()
    db.close()

    return novels

@app.get("/novels/{novel_id}/")
def get_novel_details(novel_id: int):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM novels WHERE id = ?", (novel_id,))
    novel = cursor.fetchone()
    db.close()

    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")

    return novel

@app.put("/users/profile/")
def update_profile(profile: ProfileUpdate, token: Optional[str] = None):
    user_id = verify_token(token)

    db = get_db()
    cursor = db.cursor()

    # Hash the new password if it is provided
    hashed_password = bcrypt.hashpw(profile.password.encode('utf-8'), bcrypt.gensalt()) if profile.password else None

    query = "UPDATE users SET username = ?, email = ?, password = ? WHERE id = ?"
    cursor.execute(query, (profile.username, profile.email, hashed_password, user_id))
    db.commit()
    db.close()

    return {"msg": "Profile updated successfully"}

@app.delete("/users/")
def delete_user(token: Optional[str] = None):
    user_id = verify_token(token)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    db.close()

    return {"msg": "User deleted"}

@app.get("/users/{user_id}/")
def get_user_details(user_id: int):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    db.close()

    return user

@app.get("/novels/{novel_id}/likes/")
def get_novel_likes(novel_id: int):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) AS likes FROM likes WHERE novel_id = ?", (novel_id,))
    likes = cursor.fetchone()
    db.close()

    return likes

@app.get("/novels/{novel_id}/comments/")
def get_novel_comments(novel_id: int):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM comments WHERE novel_id = ?", (novel_id,))
    comments = cursor.fetchall()
    db.close()

    return comments

@app.get("/users/{user_id}/wishlist/")
def get_user_wishlist(user_id: int):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT novels.* FROM wishlists JOIN novels ON wishlists.novel_id = novels.id WHERE wishlists.user_id = ?", (user_id,))
    wishlist = cursor.fetchall()
    db.close()

    return wishlist

@app.delete("/wishlist/{novel_id}/")
def remove_from_wishlist(novel_id: int, token: Optional[str] = None):
    user_id = verify_token(token)

    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM wishlists WHERE novel_id = ? AND user_id = ?", (novel_id, user_id))
    db.commit()
    db.close()

    return {"msg": "Novel removed from wishlist"}

@app.get("/novels/search/")
def search_novels(title: str):
    db = get_db()
    cursor = db.cursor()

    query = "SELECT * FROM novels WHERE title LIKE ?"
    cursor.execute(query, ('%' + title + '%',))
    novels = cursor.fetchall()
    db.close()

    return novels

