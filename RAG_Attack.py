import streamlit as st
import openai
import pandas as pd
import tempfile

st.title("✨🛡️ RAG Attack 🛡️✨")

# Request OpenAI API Key
api_key = st.sidebar.text_input("Enter your OpenAI API KEY", type="password")

if api_key:
    openai.api_key = api_key

    # List existing Vector Stores
    try:
        vector_stores = openai.vector_stores.list()
        vector_store_ids = [store.id for store in vector_stores.data]

        # Select an existing Vector Store
        selected_store = st.selectbox("Select an existing Vector Store", vector_store_ids)

        user_query = st.text_area("Enter your query")

        if st.button("Execute Query"):
            if not user_query:
                st.error("Please enter a query.")
            else:
                with st.spinner('Querying the Vector Store...'):
                    assistant = openai.beta.assistants.create(
                        name="RAG Assistant",
                        instructions="Use provided information to answer user's queries.",
                        tools=[{"type": "file_search"}],
                        model="gpt-3.5-turbo",
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

        st.markdown("---")
        st.subheader("Overwrite Vector Store from Excel")

        uploaded_file = st.file_uploader("Upload an Excel file to overwrite the Vector Store", type=['xlsx'])

        if st.button("Overwrite Vector Store"):
            if uploaded_file is not None:
                try:
                    df = pd.read_excel(uploaded_file)

                    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".txt") as tmp:
                        df.to_json(tmp.name, orient='records', lines=True, force_ascii=False)

                    # Delete existing Vector Store
                    openai.vector_stores.delete(selected_store)
                    st.warning(f"Vector Store '{selected_store}' deleted successfully.")

                    # Create new Vector Store
                    new_vector_store = openai.vector_stores.create(name=selected_store)

                    # Upload file to new Vector Store
                    with open(tmp.name, "rb") as file:
                        openai.vector_stores.files.upload_and_poll(
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
