\# BOT GPT 🤖



A production-grade conversational AI backend built with FastAPI, SQLite, and Groq (Llama 3.3).



\## What is this?

BOT GPT is a REST API backend that powers a ChatGPT-like experience. It supports:

\- Multi-turn conversations with an AI

\- Conversation history persistence

\- RAG (Retrieval-Augmented Generation) mode for document-grounded chat

\- Token-aware context management (sliding window)



\## Tech Stack

\- \*\*FastAPI\*\* — REST API framework

\- \*\*SQLite\*\* — Database for persistence

\- \*\*SQLAlchemy\*\* — ORM for database models

\- \*\*Groq + Llama 3.3\*\* — LLM provider

\- \*\*Pytest\*\* — Unit testing

\- \*\*Docker\*\* — Containerization

\- \*\*GitHub Actions\*\* — CI/CD pipeline



\## Project Structure

```

bot-gpt/

├── app/

│   ├── main.py        # App entry point

│   ├── models.py      # Database tables

│   ├── schemas.py     # Request/response shapes

│   ├── routes.py      # API endpoints

│   ├── database.py    # DB connection

│   └── rag.py         # RAG simulation

├── tests/

│   └── test\_api.py    # Unit tests

├── Dockerfile

├── requirements.txt

└── README.md

```



\## How to Run Locally



\### 1. Clone the repo

```

git clone https://github.com/mrunali-nilgirwar/bot-gpt.git

cd bot-gpt

```



\### 2. Create virtual environment

```

python -m venv venv

venv\\Scripts\\activate

```



\### 3. Install dependencies

```

pip install -r requirements.txt

```



\### 4. Add your Groq API key

Create a `.env` file:

```

GROQ\_API\_KEY=your\_groq\_api\_key\_here

```



\### 5. Run the app

```

uvicorn app.main:app --reload

```



\### 6. Open API docs

```

http://127.0.0.1:8000/docs

```



\## API Endpoints



| Method | Endpoint | Description |

|--------|----------|-------------|

| POST | /users | Create a new user |

| POST | /conversations | Start a new conversation |

| GET | /conversations?user\_id=1 | List all conversations for a user |

| GET | /conversations/{id} | Get full conversation with messages |

| POST | /conversations/{id}/messages | Send a message and get AI reply |

| POST | /conversations/{id}/rag-messages | Send a RAG grounded message |

| DELETE | /conversations/{id} | Delete a conversation |



\## Running Tests

```

pytest tests/ -v

```



\## Run with Docker

```

docker build -t bot-gpt .

docker run -p 8000:8000 --env GROQ\_API\_KEY=your\_key bot-gpt

```



\## Architecture

\- \*\*API Layer\*\* — FastAPI handles all HTTP requests

\- \*\*Service Layer\*\* — Routes handle business logic

\- \*\*Persistence Layer\*\* — SQLite via SQLAlchemy

\- \*\*LLM Integration\*\* — Groq API with Llama 3.3 70B model

\- \*\*RAG\*\* — Keyword-based retrieval from knowledge base

\- \*\*Context Management\*\* — Sliding window of last 10 messages



