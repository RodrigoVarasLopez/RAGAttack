import streamlit as st
import openai
import pandas as pd
import tempfile

# App Title
st.title("🔑 RAG Attack 🕵️‍♂️✨")

# App Description
st.markdown("""
**RAG Attack** allows you to interact with your OpenAI Vector Stores (RAGs).  
Enter your OpenAI API Key to query, view, or overwrite your Vector Stores easily and securely.
""")

# Initialize session state
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False

if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

if 'assistant_id' not in st.session_state:
    st.session_state.assistant_id = None

# Input API Key
api_key_input = st.text_input("Enter your OpenAI API KEY", type="password")

if st.button("Validate API Key"):
    if api_key_input:
        openai.api_key = api_key_input
        try:
            openai.models.list()
            st.session_state.api_key_valid = True
            st.session_state.api_key = api_key_input
            st.success("API Key is valid. You can now proceed with RAG Attack functionalities.")
        except Exception:
            st.session_state.api_key_valid = False
            st.error("Invalid API Key. Please enter a valid OpenAI API Key.")
    else:
        st.error("Please enter your API KEY before validating.")

# Proceed only if API key is validated
if st.session_state.api_key_valid:
    openai.api_key = st.session_state.api_key

    try:
        vector_stores = openai.vector_stores.list()
        vector_store_ids = [store.id for store in vector_stores.data]

        if vector_store_ids:
            selected_store = st.selectbox("Select an existing Vector Store", vector_store_ids)

            user_query = st.text_area("Enter your query")

            if st.button("Execute Query"):
                if not user_query:
                    st.error("Please enter a query.")
                else:
                    with st.spinner("Querying the Vector Store..."):
                        try:
                            if st.session_state.assistant_id:
                                assistant = openai.beta.assistants.retrieve(st.session_state.assistant_id)
                            else:
                                assistant = openai.beta.assistants.create(
                                    name="RAG Assistant",
                                    instructions="Use provided information to answer user's queries.",
                                    tools=[{"type": "file_search"}],
                                    model="gpt-3.5-turbo",
                                    tool_resources={"file_search": {"vector_store_ids": [selected_store]}}
                                )
                                st.session_state.assistant_id = assistant.id

                            # Ensure assistant is linked correctly
                            openai.beta.assistants.update(
                                assistant_id=assistant.id,
                                tool_resources={"file_search": {"vector_store_ids": [selected_store]}}
                            )

                            thread = openai.beta.threads.create()
                            openai.beta.threads.messages.create(
                                thread_id=thread.id,
                                role="user",
                                content=user_query
                            )

                            run = openai.beta.threads.runs.create_and_poll(
                                thread_id=thread.id,
                                assistant_id=assistant.id
                            )

                            if run.status == "completed":
                                messages = openai.beta.threads.messages.list(thread_id=thread.id)
                                response = messages.data[0].content[0].text.value
                                st.success("Results retrieved successfully")
                                st.write(response)
                            else:
                                st.error("An error occurred while retrieving the response.")
                        except Exception as e:
                            st.error(f"An error occurred during query execution: {e}")

            st.markdown("---")
            st.subheader("Overwrite Vector Store from Excel")

           # Overwrite Vector Store from Excel
uploaded_file = st.file_uploader("Upload an Excel file to overwrite the Vector Store", type=['xlsx'])

if st.button("Overwrite Vector Store"):
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)

            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt") as tmp:
                df.to_json(tmp.name, orient='records', lines=True, force_ascii=False)

            # Retrieve original Vector Store name
            original_store = openai.vector_stores.retrieve(selected_store)
            original_store_name = original_store.name

            # Delete existing Vector Store
            openai.vector_stores.delete(selected_store)
            st.warning(f"Vector Store '{original_store_name}' deleted successfully.")

            # Re-create Vector Store explicitly using original name
            new_vector_store = openai.vector_stores.create(name=original_store_name)
            st.success(f"New Vector Store '{original_store_name}' created successfully.")

            # Remove any residual files (if any, for complete safety)
            existing_files = openai.vector_stores.files.list(new_vector_store.id)
            for file in existing_files.data:
                openai.vector_stores.files.delete(
                    vector_store_id=new_vector_store.id,
                    file_id=file.id
                )

            # Upload the new file (clean upload)
            with open(tmp.name, "rb") as file:
                openai.vector_stores.files.upload_and_poll(
                    vector_store_id=new_vector_store.id,
                    file=file
                )

            st.success("Vector Store overwritten and updated successfully.")

            # Update assistant to link with the new Vector Store
            if st.session_state.assistant_id:
                openai.beta.assistants.update(
                    assistant_id=st.session_state.assistant_id,
                    tool_resources={"file_search": {"vector_store_ids": [new_vector_store.id]}}
                )
                st.success("Assistant updated successfully with the new Vector Store.")

        except Exception as e:
            st.error(f"Error during overwrite: {e}")
    else:
        st.error("Please upload an Excel file first.")

        else:
            st.info("No Vector Stores found in your account.")
    except Exception as e:
        st.error(f"An error occurred while listing Vector Stores: {e}")
