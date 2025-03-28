import streamlit as st
from openai import OpenAI, NotFoundError
import pandas as pd
import tempfile

st.title("✨🛡️ RAG Attack 🛡️✨")

# Solicitar al usuario la API Key al inicio del prompt
api_key = st.sidebar.text_input("🔑 Introduce tu API KEY de OpenAI", type="password")

if api_key:
    client = OpenAI(api_key=api_key)

    # Obtener lista de Vector Stores existentes
    try:
        vector_stores = client.vector_stores.list()
        vector_store_ids = [store.id for store in vector_stores.data]

        # Selección de Vector Store desde la lista
        selected_store = st.selectbox("📂 Selecciona una Vector Store existente", vector_store_ids)

        consulta_usuario = st.text_area("📝 Introduce tu consulta")

        if st.button("🚀 Realizar Consulta"):
            if not consulta_usuario:
                st.error("❗ Por favor introduce una consulta.")
            else:
                assistant = client.beta.assistants.create(
                    name="RAG Assistant",
                    instructions="Utiliza la información proporcionada para responder a las consultas del usuario.",
                    tools=[{"type": "file_search"}],
                    model="gpt-3.5-turbo",
                    tool_resources={"file_search": {"vector_store_ids": [selected_store]}}
                )

                thread = client.beta.threads.create()
                client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=consulta_usuario
                )

                run = client.beta.threads.runs.create_and_poll(
                    thread_id=thread.id,
                    assistant_id=assistant.id
                )

                if run.status == "completed":
                    messages = client.beta.threads.messages.list(thread_id=thread.id)
                    response = messages.data[0].content[0].text.value
                    st.success("✅ Resultados obtenidos exitosamente")
                    st.write(response)
                else:
                    st.error("❌ Error al obtener la respuesta desde la Vector Store.")

        st.markdown("---")
        st.subheader("🔄 Sobrescribir Vector Store desde Excel")

        uploaded_file = st.file_uploader("📥 Sube un archivo Excel para sobrescribir la Vector Store", type=['xlsx'])

        if st.button("♻️ Sobrescribir Vector Store"):
            if uploaded_file is not None:
                try:
                    df = pd.read_excel(uploaded_file)

                    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt") as tmp:
                        df.to_json(tmp.name, orient='records', lines=True, force_ascii=False)

                        client.vector_stores.delete(vector_store_id=selected_store)
                        st.warning(f"🗑️ Vector Store '{selected_store}' eliminada correctamente.")

                        new_vector_store = client.vector_stores.create(name=selected_store)

                        with open(tmp.name, "rb") as file:
                            client.vector_stores.files.upload_and_poll(
                                vector_store_id=new_vector_store.id,
                                file=file
                            )
                        st.success("✅ Vector Store sobrescrita y actualizada correctamente.")

                except Exception as e:
                    st.error(f"❌ Error durante la sobrescritura: {e}")
            else:
                st.error("❗ Por favor sube un archivo Excel primero.")

    except Exception as e:
        st.error(f"❌ Ha ocurrido un error al listar las Vector Stores: {e}")
else:
    st.sidebar.warning("⚠️ Por favor, introduce tu API KEY para continuar.")