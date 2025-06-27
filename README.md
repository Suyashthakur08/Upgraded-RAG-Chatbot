# Advanced RAG Chatbot (Forked & Upgraded)

This project is a significant architectural upgrade of an existing chatbot application. The original general-purpose chatbot has been transformed into a powerful, document-aware RAG (Retrieval-Augmented Generation) system capable of becoming an expert on any PDF documents provided to it.

## Fork Information and Original Credits

This repository is a fork and heavy modification of the original 'Chatbot' project created by **mherenow**. All credit for the original application structure and concept goes to them.

You can find the original repository here: [https://github.com/mherenow/Chatbot](https://github.com/mherenow/Chatbot)

## Key Upgrades and Features Implemented

The following major upgrades were performed on the original codebase:

-   **Implemented a Full RAG Pipeline:** Added the capability to upload PDF documents, which are then processed, chunked, and embedded to form a knowledge base.
-   **Replaced File Storage with a Persistent Database:** Swapped out the temporary, file-based conversation storage with a robust, persistent **PostgreSQL + pgvector** database running in Docker. This ensures both document knowledge and conversations are not lost on restart.
-   **Integrated LangChain Framework:** The entire backend logic was refactored to use LangChain, leveraging its powerful abstractions for document loading, text splitting, embeddings, memory, and conversational chains.
-   **Migrated LLM from Groq to Google Gemini:** The core AI engine was switched to use Google's Gemini models via the `langchain-google-genai` library.
-   **Revamped Frontend:** The UI and frontend logic were completely rebuilt to support the new RAG workflow, including file uploads and session management.

## Tech Stack (Upgraded Version)

-   **Backend**: Python, FastAPI
-   **AI Framework**: LangChain
-   **LLM**: Google Gemini
-   **Database**: PostgreSQL with `pgvector` extension (via Docker)
-   **Frontend**: HTML, CSS, vanilla JavaScript
-   **API Server**: Uvicorn

## Setup and Installation

### Prerequisites

-   Python 3.9+
-   Docker and Docker Compose
-   A Google Gemini API Key

### Step 1: Clone and Set Up the Environment

1.  **Clone the repository.**
    ```bash
    git clone <your-repo-url>
    cd Chatbot-Upgraded # Or your new folder name
    ```

2.  **Create and activate a Python virtual environment.**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required Python packages.**
    ```bash
    pip install -r requirements.txt
    ```

### Step 2: Configure Environment Variables

1.  Create a `.env` file in the root directory.
2.  Add your API key and database credentials:
    ```env
    # .env
    GOOGLE_API_KEY="your_google_api_key_here"

    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=chatbot_db
    DB_USER=myuser
    DB_PASSWORD=mypassword
    ```

### Step 3: Start the Database

1.  Make sure Docker Desktop is running.
2.  From the root directory, start the PostgreSQL container:
    ```bash
    docker-compose up -d
    ```

### Step 4: Run the Application

1.  Start the FastAPI backend server from the root directory:
    ```bash
    uvicorn app.main:app --reload
    ```
2.  Open your web browser and navigate to: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## How to Use

1.  The web interface will load with an upload panel on the left.
2.  Select one or more PDF files you want the chatbot to learn about.
3.  Click the "Upload & Process" button. This will create a new chat session and embed the document content.
4.  Once processing is successful, the chat input on the right will become active.
5.  Ask questions about the content of your uploaded documents.