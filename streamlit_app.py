import streamlit as st
import requests

st.title("🎤 Transcription Audio avec Whisper et autres API")

# Upload de fichier
audio_file = st.file_uploader("Choisir un fichier audio", type=["mp3", "wav", "m4a"])

# Choisir le modèle
model_option = st.selectbox("Choisir le modèle", ["whisper", "gemini", "wav2vec"])

# Si le modèle Whisper est sélectionné, choisir la langue
language = None
if model_option == "whisper":
    language = st.selectbox("Choisir la langue pour Whisper", ["ar", "fr", "en", "es", "de"])

if audio_file is not None:
    if st.button("Transcrire"):
        with st.spinner("Transcription en cours..."):
            # Préparer le fichier
            files = {'file': (audio_file.name, audio_file, audio_file.type)}

            # Utiliser data=... au lieu de json=...
            form_data = {
                "model": model_option
            }
            if model_option == "whisper" and language:
                form_data["language"] = language

            try:
                response = requests.post(
                    "https://transcription-api.iits.ma/api/audio/upload_and_transcribe",
                    files=files,
                    data=form_data  # ✅ Important : multipart/form-data
                )

                if response.status_code == 200:
                    data = response.json()
                    st.success("Transcription réussie !")
                    st.markdown("**Texte :**")
                    st.write(data.get("transcription", ""))
                    st.markdown(f"**Modèle utilisé :** {data.get('model_used', 'inconnu')}")
                    st.markdown(f"**Langue détectée :** {data.get('language', 'inconnue')}")
                else:
                    st.error(f"Erreur : {response.json().get('error', 'transcription échouée')}")
            except Exception as e:
                st.error(f"Erreur de connexion à l'API : {e}")
