import sqlite3

def get_connection():
    return sqlite3.connect("car_rental.db")  # le fichier sera créé automatiquement

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Table véhicules
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicle (
        id INTEGER PRIMARY KEY,
        marque TEXT,
        modele TEXT,
        categorie TEXT,
        tarif REAL,
        disponible INTEGER
    )
    """)

    # Table clients
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer (
        id INTEGER PRIMARY KEY,
        nom TEXT,
        prenom TEXT,
        age INTEGER,
        permis INTEGER
    )
    """)

    # Table locations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rental (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        vehicle_id INTEGER,
        start_date TEXT,
        end_date TEXT,
        total_cost REAL
    )
    """)

    conn.commit()
    conn.close()
