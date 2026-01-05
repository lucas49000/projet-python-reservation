from database import init_db, get_connection

init_db()  # crée la base et les tables si elles n'existent pas

conn = get_connection()
cursor = conn.cursor()

# Exemple : ajouter un véhicule
cursor.execute(
    "INSERT INTO vehicle VALUES (?, ?, ?, ?, ?, ?)",
    (1, "Peugeot", "208", "Voiture", 40, 1)
)

# Exemple : ajouter un client
cursor.execute(
    "INSERT INTO customer VALUES (?, ?, ?, ?, ?)",
    (1, "Raimbaut", "Lucas", 18, 1)
)

conn.commit()

# Lire les véhicules
cursor.execute("SELECT * FROM vehicle")
print(cursor.fetchall())

conn.close()
