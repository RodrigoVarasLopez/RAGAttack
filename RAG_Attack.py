import streamlit as st
from openai import OpenAI, NotFoundError
import pandas as pd
import tempfile

st.title("RAG Attack")

# Request user's OpenAI API Key
api_key = st.sidebar.text_input("Enter your OpenAI API KEY", type="password")

if api_key:
    client = OpenAI(api_key=api_key)

    # Fetch existing Vector Stores
    try:
        vector_stores = client.vector_stores.list()
        vector_store_ids = [store.id for store in vector_stores.data]

        # Vector Store selection
        selected_store = st.selectbox("Select an existing Vector Store", vector_store_ids)

        user_query = st.text_area("Enter your query")

        if st.button("Execute Query"):
            if not user_query:
                st.error("Please enter a query.")
            else:
                assistant = client.beta.assistants.create(
                    name="RAG Assistant",
                    instructions="Use the provided information to respond to user queries.",
                    tools=[{"type": "file_search"}],
                    model="gpt-3.5-turbo",
                    tool_resources={"file_search": {"vector_store_ids": [selected_store]}}
                )

                thread = client.beta.threads.create()
                client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_query
                )

                run = client.beta.threads.runs.create_and_poll(
                    thread_id=thread.id,
                    assistant_id=assistant.id
                )

                if run.status == "completed":
                    messages = client.beta.threads.messages.list(thread_id=thread.id)
                    response = messages.data[0].content[0].text.value
                    st.success("Results retrieved successfully")
                    st.write(response)
                else:
                    st.error("An error occurred while retrieving the response from the Vector Store.")

        st.markdown("---")
        st.subheader("Overwrite Vector Store from Excel")

        uploaded_file = st.file_uploader("Upload an Excel file to overwrite the Vector Store", type=['xlsx'])

        if st.button("Overwrite Vector Store"):
            if uploaded_file is not None:
                try:
                    df = pd.read_excel(uploaded_file)

                    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt") as tmp:
                        df.to_json(tmp.name, orient='records', lines=True, force_ascii=False)

                        client.vector_stores.delete(vector_store_id=selected_store)
                        st.warning(f"Vector Store '{selected_store}' has been deleted successfully.")

                        new_vector_store = client.vector_stores.create(name=selected_store)

                        with open(tmp.name, "rb") as file:
                            client.vector_stores.files.upload_and_poll(
                                vector_store_id=new_vector_store.id,
                                file=file
                            )
                        st.success("Vector Store overwritten and updated successfully.")

                except Exception as e:
                    st.error(f"Error during overwrite: {e}")
            else:
                st.error("Please upload an Excel file first.")

    except Exception as e:
        st.error(f"An error occurred while listing Vector Stores: {e}")
else:
    st.sidebar.warning("Please enter your API KEY to continue.")
