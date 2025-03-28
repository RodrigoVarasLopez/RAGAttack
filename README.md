# ✨🛡️ RAG Attack 🛡️✨

A web application built with Streamlit to easily query and overwrite Vector Stores using the OpenAI API. Ideal for systems based on RAG (Retrieval-Augmented Generation).

## 📋 Features

- **Query existing Vector Stores** using natural language.
- **Overwrite and update Vector Stores** by directly uploading Excel files.
- Simple and intuitive interface.

## ⚙️ Prerequisites

- Python 3.8 or higher
- An account at [OpenAI](https://platform.openai.com/) with API access and a valid API key

## 🚀 Installation

1. Clone this repository:

```bash
git clone https://github.com/RodrigoVarasLopez/RAGAttack.git
cd RAGAttack
```

2. Install dependencies:

```bash
pip install streamlit openai pandas openpyxl
```

## 🛠️ Configuration

- Prepare your API key from [OpenAI](https://platform.openai.com/api-keys).
- The API key will be requested from the user interface when starting the application.

## 💻 Running the Application

```bash
streamlit run rag_attack.py
```

A new window will automatically open in your default browser at `http://localhost:8501`.

## 📖 Application Usage

1. Enter your **OpenAI API KEY** in the sidebar.
2. Select an existing **Vector Store** from the dropdown menu.
3. Write your query in natural language and click on `🚀 Perform Query`.
4. To overwrite an existing Vector Store, upload your Excel file using the provided uploader and click on `♻️ Overwrite Vector Store`.

## 📂 Excel File Format for Overwriting

Your Excel file should have a clear format with relevant columns based on your information. A structure where each row represents a record to store in the Vector Store is recommended.

**Example:**

| title  | content                     |
|--------|-----------------------------|
| Recipe | Ingredients and preparation |

## 🧑‍💻 Author

Created and maintained by Rodrigo Varas(https://github.com/RodrigoVarasLopez).

## 📜 License

This project is licensed under the MIT License 

