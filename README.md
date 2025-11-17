# AI-Sound-Tutor
AI Sound Tutor - Class 9 NCERT Chapter 11 (RAG + Image Retrieval)


## Features
- Upload NCERT Sound chapter PDF
- Ask questions → get accurate answers from the chapter
- Automatically shows relevant diagrams with every answer

## Tech Stack
- Backend: FastAPI + Groq (Llama-3.3-70b) + Sentence-Transformers (local embeddings)
- Frontend: React
- RAG: Local chunking + cosine similarity
- Image Retrieval: Embedding similarity on title/description/keywords

## How to Run
```bash
# Backend
cd Backend
pip install -r requirements.txt
python -m uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm start
