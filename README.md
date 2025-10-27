# 🚀 RefactoAI – AI-Powered Clean Code Trainer

RefactoAI is a full-stack web platform and AI assistant designed to help developers master **software design patterns**, **clean code practices**, and **refactoring skills** through **various exercises**.

The system combines a **FastAPI backend** for data management and code execution with a **React + Vite frontend** for an interactive learning experience.  
It leverages **static analysis**, **AI feedback**, and **live code testing** to create an environment where developers can continuously improve code quality and reasoning.

---

## ✨ Features

- 🧠 **AI Code Review Assistant**  
  Automatically analyzes submitted code using Pylint and an AI model, providing structured, educational feedback and improvement hints.

- 🧩 **Interactive Refactoring Tasks**  
  Each challenge presents a piece of “messy code” and asks users to refactor it based on design patterns (e.g., Factory, Adapter, Strategy).

- ⚙️ **Real-Time Code Execution**  
  Run your Python code in a controlled sandbox environment and receive instant feedback.

- 📚 **Topic-Based Roadmap**  
  Tasks are grouped by programming patterns or principles, allowing learners to progress from beginner to advanced topics.

- 💬 **AI Chat Support**  
  Users can discuss code with an AI assistant trained to explain best practices and clean code concepts.

---

## 🧱 Tech Stack

### Backend
- **FastAPI** – High-performance Python web framework  
- **SQLAlchemy** – ORM for database modeling  
- **SQLite** – Lightweight local database  
- **Pylint** – Static analysis tool for Python code  

### Frontend
- **React + Vite** – Fast modern frontend framework  
- **TailwindCSS** – Utility-first CSS styling  
- **TypeScript** – Type-safe codebase  
- **Monaco Editor** – Coding environment  

### AI Layer
- **OpenAI Integration**  
  The system uses an LLM to interpret Pylint feedback, identify design issues, and provide conceptual explanations.

---

## 🧠 How It Works

1. **Task Retrieval** – The user selects a programming task from a categorized roadmap.  
2. **Code Submission** – The user writes or refactors Python code.  
3. **Code Check** – The system runs:
   - **Static analysis (Pylint)** to detect code quality issues  
   - **AI Evaluation** using LLM for conceptual and structural guidance  
4. **Feedback Delivery** – The assistant returns structured JSON feedback containing:
   - A summary of weaknesses  
   - Hints with explanations  
   - A numerical score for code clarity and structure  

---

## ⚙️ Setup Instructions

### 🔹 Backend Setup
```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn sqlalchemy python-dotenv pylint
python scripts/fill_db.py
uvicorn main:app --reload
```

### 🔹 Frontend Setup
```bash
cd client
npm install
npm run dev
```

