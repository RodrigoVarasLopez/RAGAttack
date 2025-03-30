import streamlit as st
import openai
import pandas as pd
import tempfile

# Application Title
st.title("🔑 RAG Attack 🕵️‍♂️✨")

# Brief Summary
st.markdown("""
**RAG Attack** allows you to interact with your OpenAI Vector Stores (RAGs).  
Enter your OpenAI API Key to query, view, or overwrite your Vector Stores easily and securely.
""")

# Input API Key
api_key = st.text_input("Enter your OpenAI API KEY", type="password")

if st.button("Validate API Key"):
    if api_key:
        openai.api_key = api_key

        # Verify API Key by attempting to list models
        try:
            openai.models.list()
            st.success("✅ API Key is valid. You can now proceed with RAG Attack functionalities.")

            # List existing Vector Stores
            try:
                vector_stores = openai.vector_stores.list()
                vector_store_ids = [store.id for store in vector_stores.data]

                if vector_store_ids:
                    # Select existing Vector Store
                    selected_store = st.selectbox("Select an existing Vector Store", vector_store_ids)

                    user_query = st.text_area("Enter your query")

                    if st.button("Execute Query"):
                        if not user_query:
                            st.error("Please enter a query.")
                        else:
                            with st.spinner("Querying the Vector Store..."):
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
                else:
                    st.info("No Vector Stores found in your account.")

            except Exception as e:
                st.error(f"An error occurred while listing Vector Stores: {e}")

        except Exception:
            st.error("❌ Invalid API Key. Please enter a valid OpenAI API Key.")
    else:
        st.error("⚠️ Please enter your API KEY before validating.")
