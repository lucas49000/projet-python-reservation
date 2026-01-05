import sqlite3
from database.database import init_db, get_connection

init_db()  # crée la base et les tables si elles n'existent pas

conn = get_connection()
cursor = conn.cursor()

def ajouter_vehicule(id, marque, modele, categorie, tarif, disponible):
    cursor.execute(
        "INSERT INTO vehicle VALUES (?, ?, ?, ?, ?, ?)",
        (id, marque, modele, categorie, tarif, int(disponible))
    )
    conn.commit()

ajouter_vehicule(1, "Toyota", "Corolla", "Voiture", 50.0, True)
# Exemple : ajouter un client
def ajouter_client(id, nom, prenom, age, permis):
    try:
        cursor.execute(
        "INSERT INTO customer VALUES (?, ?, ?, ?, ?)",
        (id, nom, prenom, age, int(permis)))
    except sqlite3.IntegrityError:
        print("Client avec cet ID existe déjà.")
    except sqlite3.Error as e:
        print(f"Erreur lors de l'insertion du client : {e}")

conn.commit()

# Lire les véhicules
cursor.execute("SELECT * FROM vehicle")
print(cursor.fetchall())

conn.close()
