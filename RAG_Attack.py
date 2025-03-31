import streamlit as st
import openai
import pandas as pd
import tempfile

# App Title
st.title("RAG Attack")

# Description
st.markdown("""
**RAG Attack** allows you to interact with your OpenAI Vector Stores (RAGs).  
Enter your OpenAI API Key to query, view, or overwrite your Vector Stores securely.
""")

# Session state initialization
for key in ['api_key_valid', 'api_key', 'assistant_id']:
    if key not in st.session_state:
        st.session_state[key] = None

# API Key input
api_key_input = st.text_input("Enter your OpenAI API KEY", type="password")

if st.button("Validate API Key"):
    if api_key_input:
        openai.api_key = api_key_input
        try:
            openai.models.list()
            st.session_state.api_key_valid = True
            st.session_state.api_key = api_key_input
            st.success("API Key is valid.")
        except:
            st.session_state.api_key_valid = False
            st.error("Invalid API Key.")
    else:
        st.error("Please enter your API KEY first.")

# Main functionalities
if st.session_state.api_key_valid:
    openai.api_key = st.session_state.api_key

    try:
        vector_stores = openai.vector_stores.list().data
        store_options = {store.name: store.id for store in vector_stores}

        if store_options:
            selected_store_name = st.selectbox("Select Vector Store", list(store_options.keys()))
            selected_store_id = store_options[selected_store_name]

            user_query = st.text_area("Enter your query")

            if st.button("Execute Query"):
                if user_query:
                    with st.spinner("Querying Vector Store..."):
                        try:
                            if st.session_state.assistant_id:
                                assistant = openai.beta.assistants.retrieve(st.session_state.assistant_id)
                            else:
                                assistant = openai.beta.assistants.create(
                                    name="RAG Assistant",
                                    instructions="Answer queries using Vector Store data.",
                                    tools=[{"type": "file_search"}],
                                    model="gpt-3.5-turbo",
                                    tool_resources={"file_search": {"vector_store_ids": [selected_store_id]}}
                                )
                                st.session_state.assistant_id = assistant.id

                            openai.beta.assistants.update(
                                assistant_id=assistant.id,
                                tool_resources={"file_search": {"vector_store_ids": [selected_store_id]}}
                            )

                            thread = openai.beta.threads.create()
                            openai.beta.threads.messages.create(thread.id, role="user", content=user_query)

                            run = openai.beta.threads.runs.create_and_poll(thread.id, assistant_id=assistant.id)

                            if run.status == "completed":
                                messages = openai.beta.threads.messages.list(thread.id)
                                response = messages.data[0].content[0].text.value
                                st.success("Query Results")
                                st.write(response)
                            else:
                                st.error("Error retrieving the response.")
                        except Exception as e:
                            st.error(f"Error during query: {e}")
                else:
                    st.error("Enter a query first.")

            st.markdown("---")
            st.subheader("Overwrite Vector Store from Excel")

            uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx'])

            if st.button("Overwrite Vector Store"):
                if uploaded_file:
                    try:
                        df = pd.read_excel(uploaded_file)
                        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt") as tmp:
                            df.to_json(tmp.name, orient='records', lines=True, force_ascii=False)

                        # Delete existing Vector Store
                        openai.vector_stores.delete(selected_store_id)
                        st.warning(f"Deleted Vector Store '{selected_store_name}'.")

                        # Delete associated files explicitly from account
                        files_list = openai.files.list()
                        for file in files_list.data:
                            if file.filename.startswith('tmp_'):
                                openai.files.delete(file.id)

                        # Create new Vector Store
                        new_store = openai.vector_stores.create(name=selected_store_name)

                        # Upload new file
                        with open(tmp.name, "rb") as file:
                            openai.vector_stores.files.upload_and_poll(
                                vector_store_id=new_store.id,
                                file=file
                            )

                        st.success(f"Vector Store '{selected_store_name}' overwritten successfully.")

                        # Update assistant link
                        if st.session_state.assistant_id:
                            openai.beta.assistants.update(
                                assistant_id=st.session_state.assistant_id,
                                tool_resources={"file_search": {"vector_store_ids": [new_store.id]}}
                            )
                            st.success("Assistant updated with new Vector Store.")

                    except Exception as e:
                        st.error(f"Error overwriting Vector Store: {e}")
                else:
                    st.error("Upload an Excel file first.")
        else:
            st.info("No Vector Stores found.")

    except Exception as e:
        st.error(f"Error listing Vector Stores: {e}")
