import streamlit as st

# 👉 La toute première commande Streamlit
st.set_page_config(page_title="Assistant Daxium", page_icon="🤖")

# Imports
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Lire les variables depuis .env
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")



# Vérification des variables obligatoires
if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT]):
    st.error("❌ Vérifie ton fichier .env : une ou plusieurs variables sont manquantes.")
    st.stop()

# Initialiser le client Azure OpenAI
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-05-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Titre de l'application
st.title(" Assistant Daxium ")

# Initialiser l'historique de messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are an AI assistant integrated with Daxium software. Your primary role is to professionally provide accurate and clear answers about the software's functionalities and procedures. Respond directly and concisely, without mentioning sources. If the information is unavailable or the user requires additional guidance, suggest consulting the dedicated Teams channel for support."
        }
    ]

# Affichage de l'historique
for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).write(msg["content"])

# Zone de saisie utilisateur
if prompt := st.chat_input("Pose ta question sur Daxium ici..."):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # Appel Azure OpenAI avec Azure Search (RAG)
        completion = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=st.session_state.messages,
            max_tokens=800,
            temperature=0.23,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stream=False,
            extra_body={
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": AZURE_SEARCH_ENDPOINT,
                            "index_name": AZURE_SEARCH_INDEX,
                            "semantic_configuration": "default",
                            "query_type": "semantic",
                            "fields_mapping": {},
                            "in_scope": True,
                            "role_information": st.session_state.messages[0]["content"],
                            "filter": None,
                            "strictness": 3,
                            "top_n_documents": 5,
                            "authentication": {
                                "type": "api_key",
                                "key": AZURE_SEARCH_KEY
                            }
                        }
                    }
                ]
            }
        )

        # Afficher la réponse
        assistant_reply = completion.choices[0].message.content
        st.chat_message("assistant").write(assistant_reply)
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

    except Exception as e:
        st.error(f"❌ Erreur lors de l'appel Azure OpenAI : {e}")
