<div align="center">

# 📄 DocPilot

### AI-Powered Document Question Answering using Retrieval-Augmented Generation (RAG), PostgreSQL & Groq LLM

DocPilot is an AI-powered document assistant that enables users to interact with PDF documents using natural language. It combines semantic search, Retrieval-Augmented Generation (RAG), PostgreSQL, and Groq LLMs to deliver accurate, context-aware answers with source citations.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?style=for-the-badge&logo=streamlit)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?style=for-the-badge&logo=postgresql)
![Groq](https://img.shields.io/badge/Groq-LLM-black?style=for-the-badge)
![RAG](https://img.shields.io/badge/RAG-Semantic_Search-success?style=for-the-badge)

</div>

---

# 🚀 Features

| Feature | Status |
|---------|:------:|
| PDF Upload & Processing | ✅ |
| Multi-Document Support | ✅ |
| Semantic Search | ✅ |
| Retrieval-Augmented Generation (RAG) | ✅ |
| PostgreSQL Storage | ✅ |
| Source Page Citations | ✅ |
| Document Management | ✅ |
| Groq Llama 3.3 Integration | ✅ |
| Interactive Streamlit UI | ✅ |

---

# 🏗️ System Architecture

```text
                +----------------+
                | Upload PDF(s)  |
                +-------+--------+
                        |
                        ▼
             Text Extraction & Chunking
                        |
                        ▼
              Generate Embeddings
                        |
                        ▼
          Store Chunks in PostgreSQL
                        |
        -------------------------------
                        |
                User asks Question
                        |
                        ▼
         Create Query Embedding
                        |
                        ▼
        Semantic Similarity Search
                        |
                        ▼
      Retrieve Relevant Document Chunks
                        |
                        ▼
        Groq Llama 3.3 70B Versatile
                        |
                        ▼
        Context-Aware Response
        with Source Citations
```

---

# 📂 Project Structure

```text
docpilot/
│
├── app/
│   ├── chunking.py
│   ├── config.py
│   ├── database.py
│   ├── delete_document.py
│   ├── embeddings.py
│   ├── ingestion.py
│   ├── llm.py
│   ├── pipeline.py
│   ├── retrieval.py
│   ├── storage.py
│   └── __init__.py
│
├── data/
│   └── pdfs/
│
├── tests/
│
├── streamlit_app.py
├── requirements.txt
├── README.md
├── LICENSE
└── .env.example
```

---

# ⚙️ Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python |
| Frontend | Streamlit |
| Database | PostgreSQL |
| LLM | Groq Llama 3.3 70B Versatile |
| Embedding Model | all-MiniLM-L6-v2 (Sentence Transformers) |
| PDF Processing | PyMuPDF |
| Retrieval | Cosine Similarity Search |
| Architecture | Retrieval-Augmented Generation (RAG) |

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/ArindamRout07/DocPilot_AI.git
cd docpilot
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key

DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_username
DB_PASSWORD=your_database_password
```

---

## 5. Run the application

```bash
streamlit run streamlit_app.py
```

---
## 🌐 Live Demo

🚀 **Try DocPilot here:**  
**https://docpilotai-7.streamlit.app/**

No installation required—simply upload a PDF and start asking questions!

---

## 🚀 Deployment

DocPilot is deployed on **Streamlit Community Cloud** with **Neon PostgreSQL** as the cloud database and **Groq API** powering the LLM.

### Deploy Your Own Instance

1. **Fork or Clone the Repository**

```bash
git clone https://github.com/<your-username>/docpilot.git
cd docpilot
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Create a `.env` file**

```env
GROQ_API_KEY=your_groq_api_key

DB_HOST=your_neon_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

4. **Run Locally**

```bash
streamlit run streamlit_app.py
```

5. **Deploy to Streamlit Community Cloud**

- Push your project to GitHub.
- Sign in to Streamlit Community Cloud.
- Create a new app and connect your GitHub repository.
- Set the main file to `streamlit_app.py`.
- Add the following secrets in **App Settings → Secrets**:

```toml
GROQ_API_KEY = "your_groq_api_key"

DB_HOST = "your_neon_host"
DB_PORT = "5432"
DB_NAME = "your_database_name"
DB_USER = "your_database_user"
DB_PASSWORD = "your_database_password"
```

- Click **Deploy** and your application will be live in a few minutes.

# 💡 How It Works

1. Upload one or more PDF documents.
2. The documents are parsed and split into manageable text chunks.
3. Embeddings are generated for every chunk using Sentence Transformers.
4. The chunks and their embeddings are stored in PostgreSQL.
5. When a user asks a question, the query is converted into an embedding.
6. Cosine similarity search retrieves the most relevant document chunks.
7. The retrieved context is passed to the Groq Llama 3.3 70B model.
8. The LLM generates an answer using only the retrieved context.
9. The response includes source page citations for transparency.

---

# 📚 Learning Outcomes

This project demonstrates practical experience with:

- Retrieval-Augmented Generation (RAG)
- Semantic Search
- Large Language Model Integration
- Vector Embeddings
- PostgreSQL Database Design
- Prompt Engineering
- Modular Python Development
- Streamlit Application Development
- AI-powered Information Retrieval

---

# 🔮 Future Improvements

- Hybrid Search (Keyword + Semantic)
- Streaming Responses
- Conversation Memory
- Retrieval Diagnostics
- OCR Support for Scanned PDFs
- Document Collections & Workspaces
- REST API with FastAPI
- User Authentication
- Docker Support
- Cloud Deployment

---

# 🤝 Contributing

Contributions, feature requests, and bug reports are welcome.

1. Fork the repository
2. Create a new feature branch
3. Commit your changes
4. Open a Pull Request

---

# 📄 License

This project is licensed under the **MIT License**.

See the **LICENSE** file for more information.

---

# 👨‍💻 Author

**Arindam Rout**

B.Tech in Computer Science & Engineering (AI & ML)

**GitHub:** https://github.com/ArindamRout07

**LinkedIn:** https://www.linkedin.com/in/arindam-rout-7a016a353/

---

<div align="center">

### ⭐ If you found this project useful, consider giving it a star!

</div>