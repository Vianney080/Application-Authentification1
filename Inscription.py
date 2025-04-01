import streamlit as st
import sqlite3
import bcrypt
import cv2
import face_recognition
import numpy as np
from DataBase import creer_base_de_donnees
import re

def initialiser_base_de_donnees():
    connexion = sqlite3.connect("utilisateurs.db")
    curseur = connexion.cursor()
    curseur.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            username TEXT PRIMARY KEY,
            courriel TEXT NOT NULL,
            mot_de_passe BLOB NOT NULL,
            descripteur_facial BLOB
        )
    ''')
    connexion.commit()
    connexion.close()


initialiser_base_de_donnees()

with open("style.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Fonction pour hasher un mot de passe
def hasher_mot_de_passe(mot_de_passe):
    sel = bcrypt.gensalt()
    return bcrypt.hashpw(mot_de_passe.encode('utf-8'), sel)

def valider_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    else:
        return False

# Fonction pour vérifier un mot de passe hashé
def verifier_mot_de_passe(mot_de_passe, mot_de_passe_hashe):
    return bcrypt.checkpw(mot_de_passe.encode('utf-8'), mot_de_passe_hashe)

# Fonction pour ajouter un utilisateur 
def ajouter_utilisateur(username, courriel, mot_de_passe, descripteur_facial=None):
    mot_de_passe_hashe = hasher_mot_de_passe(mot_de_passe)
    connexion = sqlite3.connect("utilisateurs.db")
    curseur = connexion.cursor()
    
    if descripteur_facial is not None:
        descripteur_texte = np.array(descripteur_facial).tobytes()
    else:
        descripteur_texte = None
    
    curseur.execute('''
        INSERT INTO utilisateurs (username, courriel, mot_de_passe, descripteur_facial)
        VALUES (?, ?, ?, ?)
    ''', (username, courriel, mot_de_passe_hashe, descripteur_texte))
    connexion.commit()
    st.success("Inscription réussie ")
    connexion.close()

# Fonction pour capturer un visage 
def capturer_visage():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Impossible d'accéder à la caméra.")
        return None

    st.write("Regardez la caméra (5 secondes maximum)...")
    placeholder = st.empty()
    max_frames = 150  
    frame_count = 0

    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            st.error("Erreur lors de la capture.")
            break

       
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_reduit = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
        face_locations = face_recognition.face_locations(image_reduit)

       
        for (top, right, bottom, left) in face_locations:
            x1, y1, x2, y2 = left*4, top*4, right*4, bottom*4
            cv2.rectangle(rgb_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        
        placeholder.image(rgb_frame, channels="RGB")

        if len(face_locations) > 0:
            cap.release()
            st.success("Visage détecté !")
            return face_recognition.face_encodings(image_reduit)[0]

        frame_count += 1

    cap.release()
    st.error("Aucun visage détecté.")
    return None

#Fonction pour verifier visage existant
def verifier_visage_existe(descripteur_capturé):
    connexion = sqlite3.connect("utilisateurs.db")
    curseur = connexion.cursor()
    curseur.execute("SELECT username, descripteur_facial FROM utilisateurs WHERE descripteur_facial IS NOT NULL")
    utilisateurs = curseur.fetchall()
    connexion.close()

    for user in utilisateurs:
        username, descripteur_stocké = user
        descripteur_stocké = np.frombuffer(descripteur_stocké, dtype=np.float64)
        distance = face_recognition.face_distance([descripteur_stocké], descripteur_capturé)[0]
        if distance < 0.6:
            return username
    return None

# Fonction pour vérifier la reconnaissance faciale
def verifier_visage(descripteur_capturé):
    connexion = sqlite3.connect("utilisateurs.db")
    curseur = connexion.cursor()
    
    curseur.execute("SELECT username, descripteur_facial FROM utilisateurs WHERE descripteur_facial IS NOT NULL")
    utilisateurs = curseur.fetchall()
    
    if not utilisateurs:
        st.error("Aucun utilisateur avec reconnaissance faciale enregistré.")
        return None
    
    signatures = [np.frombuffer(user[1], dtype=np.float64) for user in utilisateurs]
    noms = [user[0] for user in utilisateurs]
    
    distances = face_recognition.face_distance(signatures, descripteur_capturé)
    min_dist_idx = np.argmin(distances)
    
    if distances[min_dist_idx] < 0.6:
        connexion.close()
        return noms[min_dist_idx]
    else:
        st.error("Visage non reconnu.")
        connexion.close()
        return None

# Fonction pour vérifier les informations de connexion
def verifier_connexion(username, mot_de_passe):
    connexion = sqlite3.connect("utilisateurs.db")
    curseur = connexion.cursor()
    
    curseur.execute('''
        SELECT mot_de_passe FROM utilisateurs WHERE username = ?
    ''', (username,))
    resultat = curseur.fetchone()
    connexion.close()
    
    if resultat and verifier_mot_de_passe(mot_de_passe, resultat[0]):
        return True
    return False

# Initialisation de la session
if 'connecte' not in st.session_state:
    st.session_state.connecte = False
    st.session_state.username = None

# Interface Streamlit
st.markdown("<h1><i class='fas fa-user-lock'></i> Application d'Authentification</h1>", unsafe_allow_html=True)
st.sidebar.markdown("### <i class='fas fa-bars'></i> Menu", unsafe_allow_html=True)

if st.session_state.connecte:
    st.success(f"Bienvenue , {st.session_state.username} ! sur la page du projet 2")
    if st.button("Se déconnecter"):
        st.session_state.connecte = False
        st.session_state.username = None
        st.success("Déconnexion réussie.")
else:
    options = {
    "📝Inscription": "Inscription",
    "🔐 Connexion": "Connexion",
    "😊 Connexion par visage": "Connexion par visage"
    }

    selection = st.sidebar.selectbox("Choisir une action", list(options.keys()))
    action = options[selection]
  

    if action == "Inscription":
        st.markdown(
            "<p style='font-size:30px; color:#2563eb; font-weight:600;'>"
            "<i class='fas fa-user-plus'></i> Inscription</p>",
            unsafe_allow_html=True
        )
        with st.form(key="formulaire_inscription"):
            username = st.text_input("Username")
            courriel = st.text_input("Courriel")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            ajouter_visage = st.checkbox("Ajouter la reconnaissance faciale")
            bouton_soumettre = st.form_submit_button(label="S'inscrire")

        if bouton_soumettre:
            if username and courriel and mot_de_passe:
                if not valider_email(courriel):
                   st.error("Veuillez entrer une adresse e-mail valide (exemple : nom@gmail.com).")

                else:
                   connexion = sqlite3.connect("utilisateurs.db")
                   if ajouter_visage:
                    
                     arreter = st.button("Arrêter la capture", key="arreter_inscription")
                     descripteur_facial = capturer_visage()
                     if descripteur_facial is not None and not arreter:
                        utilisateur_existant = verifier_visage_existe(descripteur_facial)
                        if utilisateur_existant:
                            st.error(f"Ce visage est déjà enregistré pour l'utilisateur {utilisateur_existant} !")
                        else:
                           ajouter_utilisateur(username, courriel, mot_de_passe, descripteur_facial)
                           st.success("Inscription réussie avec reconnaissance faciale !")

                   else:
                      ajouter_utilisateur(username, courriel, mot_de_passe)
                      st.success("Inscription réussie !")
            else:
                st.warning("Veuillez remplir tous les champs.")

    elif action == "Connexion":
        st.markdown(
            "<p style='font-size:30px; color:#2563eb; font-weight:600;'>"
            "<i class='fas fa-right-to-bracket'></i> Connexion</p>",
             unsafe_allow_html=True
        )
        with st.form(key="formulaire_connexion"):
            username = st.text_input("Username")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            bouton_connexion = st.form_submit_button(label="Se connecter")

            if bouton_connexion:
                if username and mot_de_passe:
                    if verifier_connexion(username, mot_de_passe):
                        st.session_state.connecte = True
                        st.session_state.username = username
                        st.success(f"Bienvenue, {username} !")
                    else:
                        st.error("Username ou mot_de_passe incorrect.")
                else:
                    st.warning("Veuillez remplir tous les champs.")

    elif action == "Connexion par visage":
        st.markdown(
            "<p style='font-size:30px; color:#2563eb; font-weight:600;'>"
             "<i class='fas fa-face-smile'></i> Connexion par visage</p>",
             unsafe_allow_html=True
        )
        if st.button("Démarrer la caméra"):
            
            arreter = st.button("Arrêter la capture", key="arreter_connexion")
            descripteur_capturé = capturer_visage()
            if descripteur_capturé is not None and not arreter:
                username = verifier_visage(descripteur_capturé)
                if username:
                    st.session_state.connecte = True
                    st.session_state.username = username
                    st.success(f"Bienvenue, {username} !")

#if st.button("Créer la base de données"):
    #creer_base_de_donnees()