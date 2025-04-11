import streamlit as st  
import cv2  
import numpy as np  
import tempfile 
import os  
from distances import RechercheImage
from descripteur import glcm, haralick_feat, bitdesc, concatenation

st.title("🔍 Trouve des images similaires")

mon_image = st.file_uploader("Choisis une image", type=["jpg", "png","jpeg"])

methode = st.selectbox("Choisis une méthode", ["GLCM", "Haralick", "BiT", "Concat"])

distance = st.selectbox("Choisis une distance", ["euclidienne", "manhattan", "chebyshev", "canberra"])




k = 10  

if mon_image is not None:
    
    fichier = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    fichier.write(mon_image.read())
    chemin_image = fichier.name

    
    st.write("Ton image :")
    image_choisie = cv2.imread(chemin_image)
    if image_choisie is not None:
        image_choisie = cv2.cvtColor(image_choisie, cv2.COLOR_BGR2RGB)
        st.image(image_choisie, caption="Image téléchargée", width=300)  
    else:
        st.write("Problème avec ton image !")

   
    image_gris = cv2.imread(chemin_image, cv2.IMREAD_GRAYSCALE)
    
   
    if image_gris is None:
        st.write("Oups, je ne peux pas lire l'image !")
    else:

        if methode == "GLCM":
            details = glcm(chemin_image)  
        elif methode == "Haralick":
            details = haralick_feat(chemin_image)
        elif methode == "BiT":
            details = bitdesc(chemin_image)
        elif methode == "Concat":
            details = concatenation(chemin_image)

       
        if methode == "GLCM":
            toutes_images = np.load("SignaturesGLCM.npy", allow_pickle=True)
        elif methode == "Haralick":
            toutes_images = np.load("SignaturesHaralick.npy", allow_pickle=True)
        elif methode == "BiT":
            toutes_images = np.load("SignaturesBiT.npy", allow_pickle=True)
        elif methode == "Concat":
            toutes_images = np.load("SignaturesConcat.npy", allow_pickle=True)

        
        resultats = RechercheImage(toutes_images, details, distance, k)  

       
        st.write("Images similaires :")
        colonnes = st.columns(4) 
        for i, (chemin, distance_valeur, _) in enumerate(resultats):
            chemin_complet = os.path.join("dataset", chemin)
            image_trouvee = cv2.imread(chemin_complet)
            if image_trouvee is not None:
                image_trouvee = cv2.cvtColor(image_trouvee, cv2.COLOR_BGR2RGB)
                with colonnes[i % 4]:  
                    st.image(image_trouvee, caption=f"Distance : {distance_valeur:.2f}", use_container_width=True)
            else:
                with colonnes[i % 4]:
                    st.write("Image manquante")


else:
    st.write("Mets une image pour commencer !")


    st.markdown(
    "<br><a href='http://localhost:8501' target='_self'>"
    "<button style='background-color:#2563eb; color:white; padding:10px 20px; border:none; border-radius:5px;'>🔙 Retour à l'accueil</button>"
    "</a>",
    unsafe_allow_html=True
)