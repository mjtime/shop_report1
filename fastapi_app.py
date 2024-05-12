from fastapi import FastAPI, HTTPException
from typing import List, Optional
import sqlite3
import bcrypt
import requests

app = FastAPI()

def create_connection():
    conn = sqlite3.connect('shopping_mall.db')
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            full_name TEXT,
            address TEXT,
            payment_info TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            price REAL,
            thumbnail_url TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buylist (
            buy_id INTEGER PRIMARY KEY,
            uid INTEGER,
            pid INTEGER,
            date TEXT DEFAULT CURRENT_TIMESTAMP,
            pay_state BOOLEAN,
            u_address TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buytid (
            buy_id INTEGER PRIMARY KEY,
            tid TEXT
        )
    ''')
    conn.commit()

def add_tid1(conn, buy_id, tid):
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO buytid (buy_id, tid) VALUES (?, ?)',(buy_id, tid))
    conn.commit()
    tiditem = {"buy_id": buy_id, "tid": tid}
    return {"message": "User created successfully!", "tiditem": tiditem}

def get_tid(conn, buy_id):
    cursor = conn.cursor()
    cursor.execute(f'SELECT tid FROM buytid WHERE buy_id=?',(buy_id,))
    buytid = cursor.fetchall()
    conn.commit()
    
    return buytid[0]

def add_user(conn, username, password, full_name, address, payment_info):
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute(f'INSERT INTO users (username, password, role, full_name, address, payment_info) VALUES (?, ?, ?, ?, ?, ?)',
                (username, hashed_password, 'user', full_name, address, payment_info))
    conn.commit()
    user = {"username": username, "password": hashed_password, "role": 'user', "full_name": full_name, "address": address, "payment_info": payment_info}
    return {"message": "User created successfully!", "user": user}

def register_admin(conn, username, password, full_name):
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute('INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)',
                (username, hashed_password, 'admin', full_name))
    conn.commit()
    user = {"username": username, "password": hashed_password, "role": 'admin', "full_name": full_name}
    return {"message": "Admin registered successfully!", "user": user}

def authenticate_user(conn, username, password):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    if user:
        stored_hashed_password = user[2]

        input_hashed_password = bcrypt.hashpw(password.encode('utf-8'), stored_hashed_password)

        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
            user_info = {"id":user[0], "username": user[1], "password": user[2], "role": user[3], "full_name": user[4], "address": user[5], "payment_info": user[6]}
            return {"message": f"Welcome back, {username}!", "user":user_info}
        else:
            raise HTTPException(status_code=401, detail="Invalid username or password")
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

def get_all_products(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    return [{ "id":product[0], "name": product[1], "category": product[2], "price": product[3], "thumbnail_url": product[4]} for product in products]

def add_product(conn, name, category, price, thumbnail_url, password):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    user = cursor.fetchone()
    if user:
        stored_hashed_password = user[2]

        input_hashed_password = bcrypt.hashpw(password.encode('utf-8'), stored_hashed_password)

        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
            cursor.execute('INSERT INTO products (name, category, price, thumbnail_url) VALUES (?, ?, ?, ?)', (name, category, price, thumbnail_url))
            conn.commit()
            return {"message": "Product added successfully!"}
        else:
            raise HTTPException(status_code=401, detail="add product error.")
    else:
        raise HTTPException(status_code=401, detail="add product error.")

def update_user_info(conn, id, full_name, address, payment_info, password):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
    user = cursor.fetchone()
    if user:
        stored_hashed_password = user[2]

        input_hashed_password = bcrypt.hashpw(password.encode('utf-8'), stored_hashed_password)

        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
            cursor.execute('UPDATE users SET full_name = ?, address = ?, payment_info = ? WHERE id = ?', (full_name, address, payment_info, id))
            conn.commit()
            return {"message": "User information updated successfully!"}
        else:
            raise HTTPException(status_code=401, detail="User information updated error.")
    else:
        raise HTTPException(status_code=401, detail="User information updated error.")




def update_buy_list1(conn, buy_id, uid, pid, date, state, u_address):
    cursor = conn.cursor()
    cursor.execute('UPDATE buylist SET uid = ?, pid = ?, date =?, pay_state=?, u_address=? WHERE buy_id = ?', (uid, pid, date, state, u_address, buy_id))
    conn.commit()
    return {"message": "buy information updated successfully!"}

def get_user_by_username(conn, username):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    return cursor.fetchone()

# 사용자 구매내역 확인
def get_user_buy_list1(conn, userid):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM buylist WHERE uid=?', (userid,))
    u_buy_lists = cursor.fetchall()
    return [{"buy_id":u_buy_list[0], "uid":u_buy_list[1], "pid": u_buy_list[2], "date": u_buy_list[3], "state": u_buy_list[4], "u_address": u_buy_list[5]} for u_buy_list in u_buy_lists]

# 구매번호로 구매내역 확인
def get_one_buy_list1(conn, buy_id):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM buylist WHERE buy_id=?', (buy_id,))
    u_buy_lists = cursor.fetchall()
    return [{"buy_id":u_buy_list[0], "uid":u_buy_list[1], "pid": u_buy_list[2], "date": u_buy_list[3], "state": u_buy_list[4], "u_address": u_buy_list[5]} for u_buy_list in u_buy_lists]


# 사용자 전체 구매내역 확인
def get_all_buy_list1(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM buylist')

    u_buy_lists = cursor.fetchall()
    return [{"buy_id":u_buy_list[0], "uid":u_buy_list[1], "pid": u_buy_list[2], "date": u_buy_list[3], "state": u_buy_list[4], "u_address": u_buy_list[5]} for u_buy_list in u_buy_lists]


# 구매내역 기록 기록
def add_buy(conn, user_id, product_id, state, address):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO buylist (uid, pid, pay_state, u_address) VALUES (?, ?, ?, ?)', (user_id, product_id, state, address))
    conn.commit()
    return {"message": "thank you for buy our product!"}

def del_buy(conn, buy_id):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM buylist WHERE buy_id = ?', (buy_id,))
    conn.commit()
    return {"message": "delete!"}


@app.on_event("startup")
async def startup_event():
    conn = create_connection()
    create_tables(conn)
    if not get_user_by_username(conn, "admin"):
        register_admin(conn, "admin", "admin", "Admin User")
    conn.close()

@app.get("/register")
async def register_user(username: str, password: str, full_name: str, address: Optional[str] = None, payment_info: Optional[str] = None):
    conn = create_connection()
    result = add_user(conn, username, password, full_name, address, payment_info)
    conn.close()
    return result

@app.get("/login")
async def login(username: str, password: str):
    conn = create_connection()
    result = authenticate_user(conn, username, password)
    conn.close()
    return result

@app.get("/products", response_model=List[dict])
async def get_products():
    conn = create_connection()
    products = get_all_products(conn)
    conn.close()
    return products

@app.get("/add_tid")
async def add_tid(buy_id: str, tid: str):
    conn = create_connection()
    result = add_tid1(conn, buy_id, tid)
    conn.close()
    return result

@app.get("/add_product")
async def add_new_product(name: str, category: str, price: float, thumbnail_url: str, pw:str):
    conn = create_connection()
    result = add_product(conn, name, category, price, thumbnail_url, pw)
    conn.close()
    return result

@app.get("/update_user_info")
async def update_user_info_endpoint(id: int, full_name: str, address: str, payment_info: str, pw:str):
    conn = create_connection()
    result = update_user_info(conn, id, full_name, address, payment_info, pw)
    conn.close()
    return result

@app.get("/update_buy_list")
async def update_buy_list(buy_id: int, uid: int, pid: int, date: str, state:int, u_address: str):
    conn = create_connection()
    result = update_buy_list1(conn, buy_id, uid, pid, date, state, u_address)
    conn.close()
    return result

# 사용자 구매 목록 요청 페이지
@app.get("/user_buy_list", response_model=List[dict])
async def get_user_buy_list(user_id: int):
    conn = create_connection()
    u_buy_lists = get_user_buy_list1(conn, user_id)
    conn.close()
    return u_buy_lists


# 구매번호로 구매목록 요청 페이지
@app.get("/one_buy_list")
async def get_one_buy_list(buy_id: int):
    conn = create_connection()
    u_buy_list = get_one_buy_list1(conn, buy_id)
    conn.close()
    return u_buy_list

# 관리자 구매 목록 요청 페이지
@app.get("/all_buy_list", response_model=List[dict])
async def get_all_buy_list():
    conn = create_connection()
    u_buy_lists = get_all_buy_list1(conn)
    conn.close()
    return u_buy_lists

# 구매 상품 추가 페이지
@app.get("/add_buy")
async def add_new_buy(user_id: int, product_id: int, state: bool, address: str):
    conn = create_connection()
    result = add_buy(conn, user_id, product_id, state, address)
    conn.close()
    return result


@app.get("/del_buy_list")
async def del_buy_list(buy_id: int):
    conn = create_connection()
    result = del_buy(conn, buy_id)
    conn.close()
    return result

@app.get("/kakaopay/success")
async def del_buy_list(partner_order_id: str, pg_token:str):
    conn = create_connection()
    tid = get_tid(conn, partner_order_id)
    conn.close()
    URL = 'https://kapi.kakao.com/v1/payment/approve'
    headers = {
        "Authorization": "KakaoAK " + "21b689f29d862ef635c0be7437dd8575",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "cid": "TC0ONETIME",  # 테스트용 코드
        "tid": tid,  # 결제 요청시 세션에 저장한 tid
        "partner_order_id": partner_order_id,  # 주문번호
        "partner_user_id": "testuser",  # 유저 아이디
        "pg_token": pg_token,  # 쿼리 스트링으로 받은 pg토큰
    }

    res = requests.post(URL, headers=headers, params=params)

    return {"message": res.text}

@app.get("/kakaopay/fail")
async def del_buy_list(buy_id: int):
    return {"message": "buy fail!"}
@app.get("/kakaopay/cancel")
async def del_buy_list(buy_id: int):
    return {"message": "buy cancel!"}