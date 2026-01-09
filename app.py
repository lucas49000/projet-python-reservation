import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# Configuration de la page
st.set_page_config(
    page_title="Gestion Location de Véhicules",
    page_icon="🚗",
    layout="wide"
)

#  Gestion de la base de données 
DB_FILE = "car_rental.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    """Initialise la base de données selon votre schéma database.py"""
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

# Initialisation au lancement
init_db()

#  Fonctions utilitaires pour récupérer les données 

def get_vehicles(only_available=False):
    conn = get_connection()
    query = "SELECT * FROM vehicle"
    if only_available:
        query += " WHERE disponible = 1"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_customers():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM customer", conn)
    conn.close()
    return df

def get_rentals():
    conn = get_connection()
    # Jointure pour avoir les noms des clients et véhicules au lieu des IDs
    query = """
    SELECT 
        r.id, 
        c.nom || ' ' || c.prenom as client, 
        v.marque || ' ' || v.modele as vehicule, 
        r.start_date, 
        r.end_date, 
        r.total_cost,
        r.vehicle_id
    FROM rental r
    JOIN customer c ON r.customer_id = c.id
    JOIN vehicle v ON r.vehicle_id = v.id
    ORDER BY r.id DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

#  Interface Utilisateur Streamlit 

# Barre latérale de navigation
st.sidebar.title("🚗 Navigation")
page = st.sidebar.radio("Aller vers", ["Tableau de bord", "Véhicules", "Clients", "Nouvelle Location", "Historique Locations"])

st.sidebar.markdown("---")
st.sidebar.info("Système de gestion v1.0")

# Tableau de bord
if page == "Tableau de bord":
    st.title("📊 Tableau de Bord")
    
    col1, col2, col3 = st.columns(3)
    
    df_v = get_vehicles()
    df_c = get_customers()
    df_r = get_rentals()
    
    total_revenu = df_r['total_cost'].sum() if not df_r.empty else 0
    vehicules_dispo = df_v[df_v['disponible'] == 1].shape[0] if not df_v.empty else 0
    
    col1.metric("Véhicules Disponibles", f"{vehicules_dispo} / {len(df_v)}")
    col2.metric("Clients Enregistrés", len(df_c))
    col3.metric("Chiffre d'Affaires", f"{total_revenu:.2f} €")
    
    st.divider()
    
    # Graphique simple de répartition
    if not df_v.empty:
        st.subheader("Répartition de la flotte par catégorie")
        category_counts = df_v['categorie'].value_counts()
        st.bar_chart(category_counts)

# Véhicules
elif page == "Véhicules":
    st.title("🚙 Gestion de la Flotte")
    
    tab1, tab2 = st.tabs(["Liste des Véhicules", "Ajouter un Véhicule"])
    
    with tab1:
        df = get_vehicles()
        if not df.empty:
            # Formatage pour l'affichage (Oui/Non au lieu de 1/0)
            df['disponible'] = df['disponible'].apply(lambda x: "✅ Oui" if x == 1 else "❌ Non")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Aucun véhicule dans la base.")
            
    with tab2:
        st.subheader("Nouveau Véhicule")
        with st.form("add_vehicle_form"):
            c1, c2 = st.columns(2)
            id_veh = c1.number_input("ID Véhicule (Unique)", min_value=1, step=1)
            tarif = c2.number_input("Tarif Journalier (€)", min_value=0.0, step=5.0)
            
            c3, c4, c5 = st.columns(3)
            marque = c3.text_input("Marque")
            modele = c4.text_input("Modèle")
            categorie = c5.selectbox("Catégorie", ["Voiture", "Camion", "Moto", "Utilitaire"])
            
            submitted = st.form_submit_button("Ajouter le véhicule")
            
            if submitted:
                conn = get_connection()
                try:
                    conn.execute(
                        "INSERT INTO vehicle (id, marque, modele, categorie, tarif, disponible) VALUES (?, ?, ?, ?, ?, ?)",
                        (id_veh, marque, modele, categorie, tarif, 1)
                    )
                    conn.commit()
                    st.success(f"{marque} {modele} ajouté avec succès !")
                except sqlite3.IntegrityError:
                    st.error("Erreur : Un véhicule avec cet ID existe déjà.")
                except Exception as e:
                    st.error(f"Erreur : {e}")
                finally:
                    conn.close()

# Clients
elif page == "Clients":
    st.title("👤 Gestion des Clients")
    
    tab1, tab2 = st.tabs(["Liste des Clients", "Ajouter un Client"])
    
    with tab1:
        df = get_customers()
        st.dataframe(df, use_container_width=True)
        
    with tab2:
        st.subheader("Nouveau Client")
        with st.form("add_client_form"):
            c1, c2 = st.columns(2)
            id_client = c1.number_input("ID Client (Unique)", min_value=1, step=1)
            age = c2.number_input("Âge", min_value=18, max_value=100)
            
            c3, c4 = st.columns(2)
            prenom = c3.text_input("Prénom")
            nom = c4.text_input("Nom")
            
            permis = st.checkbox("Possède un permis valide ?", value=True)
            
            submitted = st.form_submit_button("Ajouter le client")
            
            if submitted:
                if not nom or not prenom:
                    st.error("Nom et Prénom sont obligatoires.")
                else:
                    conn = get_connection()
                    try:
                        conn.execute(
                            "INSERT INTO customer (id, nom, prenom, age, permis) VALUES (?, ?, ?, ?, ?)",
                            (id_client, nom, prenom, age, int(permis))
                        )
                        conn.commit()
                        st.success(f"Client {prenom} {nom} ajouté !")
                    except sqlite3.IntegrityError:
                        st.error("Erreur : Un client avec cet ID existe déjà.")
                    finally:
                        conn.close()

# Nouvelle Location
elif page == "Nouvelle Location":
    st.title("🔑 Créer une Location")
    
    # Récupération des données pour les listes déroulantes
    conn = get_connection()
    clients = pd.read_sql("SELECT id, nom, prenom, permis FROM client", conn)
    # Seuls les véhicules disponibles
    vehicules = pd.read_sql("SELECT id, marque, modele, tarif FROM vehicle WHERE disponible = 1", conn)
    conn.close()
    
    if clients.empty or vehicules.empty:
        st.warning("Il vous faut au moins un client et un véhicule disponible pour créer une location.")
    else:
        # Création des dictionnaires pour les sélections conviviales
        client_options = {f"{row['prenom']} {row['nom']} (ID: {row['id']})": row['id'] for index, row in clients.iterrows()}
        vehicule_options = {f"{row['marque']} {row['modele']} - {row['tarif']}€/j (ID: {row['id']})": (row['id'], row['tarif']) for index, row in vehicules.iterrows()}
        
        with st.form("rental_form"):
            col1, col2 = st.columns(2)
            
            selected_client_label = col1.selectbox("Sélectionner le Client", list(client_options.keys()))
            selected_vehicule_label = col2.selectbox("Sélectionner le Véhicule", list(vehicule_options.keys()))
            
            col3, col4 = st.columns(2)
            start_d = col3.date_input("Date de début", min_value=date.today())
            end_d = col4.date_input("Date de fin", min_value=date.today())
            
            # Calcul préliminaire du coût
            selected_vehicule_id, tarif_journalier = vehicule_options[selected_vehicule_label]
            selected_client_id = client_options[selected_client_label]
            
            days = (end_d - start_d).days
            if days < 1: days = 1
            total_cost = days * tarif_journalier
            
            st.info(f"💰 Coût estimé pour {days} jour(s) : **{total_cost:.2f} €**")
            
            submit_rental = st.form_submit_button("Valider la Location")
            
            if submit_rental:
                
                # On récupère les infos du client sélectionné
                client_info = clients[clients['id'] == selected_client_id].iloc[0]
                
                # Si permis == 0, bloquer la location
                if client_info['permis'] == 0:
                    st.error(f" INTERDIT : {client_info['prenom']} {client_info['nom']} n'a pas de permis valide !")
                    st.stop() # Arrête le script ici
               
                if start_d > end_d:
                    st.error("La date de fin doit être après la date de début.")
                else:
                    conn = get_connection()
                    try:
                        # 1. Créer la location
                        conn.execute("""
                            INSERT INTO rental (customer_id, vehicle_id, start_date, end_date, total_cost)
                            VALUES (?, ?, ?, ?, ?)
                        """, (selected_client_id, selected_vehicule_id, str(start_d), str(end_d), total_cost))
                        
                        # 2. Mettre à jour la disponibilité du véhicule
                        conn.execute("UPDATE vehicle SET disponible = 0 WHERE id = ?", (selected_vehicule_id,))
                        
                        conn.commit()
                        st.success("Location enregistrée avec succès !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Une erreur est survenue : {e}")
                    finally:
                        conn.close()

# Historique Locations
elif page == "Historique Locations":
    st.title("📜 Historique et Retours")
    
    df_rentals = get_rentals()
    
    st.subheader("Locations en cours et passées")
    st.dataframe(df_rentals, use_container_width=True)
    
    st.divider()
    st.subheader("Retour de Véhicule")
    
    # Interface pour retourner un véhicule (le rendre disponible à nouveau)
    conn = get_connection()
    # Trouver les véhicules actuellement loués (disponible = 0)
    vehicules_loues = pd.read_sql("SELECT id, marque, modele FROM vehicle WHERE disponible = 0", conn)
    conn.close()
    
    if not vehicules_loues.empty:
        options_retour = {f"{row['marque']} {row['modele']} (ID: {row['id']})": row['id'] for index, row in vehicules_loues.iterrows()}
        
        c1, c2 = st.columns([3, 1])
        vehicule_a_rendre = c1.selectbox("Sélectionner le véhicule à restituer", list(options_retour.keys()))
        btn_rendre = c2.button("Restituer le Véhicule")
        
        if btn_rendre:
            vid_to_return = options_retour[vehicule_a_rendre]
            conn = get_connection()
            conn.execute("UPDATE vehicle SET disponible = 1 WHERE id = ?", (vid_to_return,))
            conn.commit()
            conn.close()
            st.success("Véhicule restitué et marqué comme disponible !")
            st.rerun()
    else:
        st.info("Tous les véhicules sont actuellement au garage (disponibles).")