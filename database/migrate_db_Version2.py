#!/usr/bin/env python3
"""
Migration / réparation simple de database/car_rental.db pour correspondre aux classes modifiées.

Usage:
    python3 migrate_db.py path/to/car_rental.db
"""
import sqlite3
import sys
import shutil
import datetime

def backup(db_path):
    bak = db_path + ".bak"
    shutil.copy2(db_path, bak)
    print(f"Backup créé: {bak}")

def column_exists(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    return column in cols

def table_exists(conn, table):
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table,))
    return cur.fetchone() is not None

def add_column(conn, table, column_def):
    print(f"Ajout colonne dans {table}: {column_def}")
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def};")

def ensure_vehicle_columns(conn):
    if not table_exists(conn, "vehicle"):
        print("Table 'vehicle' manquante — création d'une table minimale 'vehicle'.")
        conn.execute("""CREATE TABLE vehicle (
            id INTEGER PRIMARY KEY,
            marque TEXT,
            modele TEXT,
            categorie TEXT,
            tarif REAL,
            disponible INTEGER DEFAULT 1
        );""")
        return

    if not column_exists(conn, "vehicle", "disponible"):
        add_column(conn, "vehicle", "disponible INTEGER DEFAULT 1")
    if not column_exists(conn, "vehicle", "tarif"):
        add_column(conn, "vehicle", "tarif REAL")
    if not column_exists(conn, "vehicle", "categorie"):
        add_column(conn, "vehicle", "categorie TEXT")

    # Mettre disponible = 1 quand NULL
    conn.execute("UPDATE vehicle SET disponible = 1 WHERE disponible IS NULL;")
    print("Mise à jour: valeurs NULL de 'disponible' réglées à 1 (si présentes).")

def ensure_customer_columns(conn):
    if not table_exists(conn, "customer"):
        print("Table 'customer' manquante — création d'une table minimale 'customer'.")
        conn.execute("""CREATE TABLE customer (
            id INTEGER PRIMARY KEY,
            nom TEXT,
            prenom TEXT,
            age INTEGER,
            permis INTEGER
        );""")
        return
    # Aucune migration complexe ici ; on suppose colonnes déjà correctes.

def ensure_rental_table(conn):
    # On veut une table 'rental' (ou 'rental' remplaçant 'rental' existante) :
    desired_cols = ["id","customer_id","vehicle_id","start_date","end_date","total_cost"]
    if not table_exists(conn, "rental"):
        print("Table 'rental' introuvable — création de 'rental'.")
        conn.execute("""CREATE TABLE rental (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            vehicle_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            total_cost REAL
        );""")
        return

    # Vérifie si colonnes attendues existent ; si non, on essaie de migrer doucement
    cur = conn.execute("PRAGMA table_info(rental);")
    existing = [r[1] for r in cur.fetchall()]
    missing = [c for c in desired_cols if c not in existing]
    if not missing:
        print("Table 'rental' a le schéma attendu.")
        return

    print("Table 'rental' a un schéma différent. Création d'une nouvelle table 'rental_new' et migration des colonnes connues.")
    # Création table temporaire
    conn.execute("""CREATE TABLE IF NOT EXISTS rental_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            vehicle_id INTEGER,
            start_date TEXT,
            end_date TEXT,
            total_cost REAL
        );""")
    # Tenter de copier les colonnes compatibles si elles existent
    copy_cols = [c for c in ["customer_id","vehicle_id","start_date","end_date","total_cost"] if c in existing]
    if copy_cols:
        cols_csv = ",".join(copy_cols)
        conn.execute(f"INSERT INTO rental_new ({cols_csv}) SELECT {cols_csv} FROM rental;")
        print(f"Copié les colonnes existantes: {copy_cols}")
    else:
        print("Aucune colonne compatible à copier depuis 'rental'.")

    # Remplacer les tables
    conn.execute("ALTER TABLE rental RENAME TO rental_old;")
    conn.execute("ALTER TABLE rental_new RENAME TO rental;")
    print("Migration: 'rental' remplacée (ancienne renommée 'rental_old').")

def normalize_dates(conn):
    # Tenter de normaliser les dates dans rental (si présentes) au format YYYY-MM-DD
    if not table_exists(conn, "rental"):
        return
    cur = conn.execute("PRAGMA table_info(rental);")
    cols = [r[1] for r in cur.fetchall()]
    for col in ("start_date","end_date"):
        if col not in cols:
            continue
        rows = conn.execute(f"SELECT id, {col} FROM rental;").fetchall()
        updates = []
        for rid, val in rows:
            if val is None:
                continue
            try:
                # Essayer de parser quelques formats communs
                val_str = str(val).strip()
                # Détecter YYYY-MM-DD déjà ok
                if len(val_str) >= 10 and val_str[:10].count("-") == 2:
                    formatted = val_str[:10]
                else:
                    # Essayons plusieurs formats
                    for fmt in ("%d/%m/%Y","%Y/%m/%d","%d-%m-%Y","%d.%m.%Y","%Y.%m.%d"):
                        try:
                            dt = datetime.datetime.strptime(val_str, fmt)
                            formatted = dt.date().isoformat()
                            break
                        except Exception:
                            formatted = None
                    if formatted is None:
                        # si on ne sait pas, on laisse tel quel
                        continue
                if formatted and formatted != val_str:
                    updates.append((formatted, rid))
            except Exception:
                continue
        for f, rid in updates:
            conn.execute("UPDATE rental SET {} = ? WHERE id = ?;".format(col), (f, rid))
        if updates:
            print(f"Normalized {len(updates)} valeurs dans '{col}'.")

def main(db_path):
    backup(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        ensure_vehicle_columns(conn)
        ensure_customer_columns(conn)
        ensure_rental_table(conn)
        normalize_dates(conn)
        conn.commit()
        print("Migration terminée avec succès.")
    except Exception as e:
        conn.rollback()
        print("Erreur durant la migration:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 migrate_db.py path/to/car_rental.db")
        sys.exit(1)
    main(sys.argv[1])