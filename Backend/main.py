from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import PyPDF2
import json
import os
import shutil
import numpy as np
from pathlib import Path
import uuid

# ------------------- GROQ SETUP (FREE for LLM only) -------------------
from groq import Groq
client = Groq(api_key="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")  # tumhari key

# ------------------- LOCAL EMBEDDINGS (Free + Offline) -------------------
from sentence_transformers import SentenceTransformer
embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Free local model, fast

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
CHUNKS_DIR = BASE_DIR / "chunks"
IMAGES_DIR = BASE_DIR / "images"
IMAGE_METADATA_PATH = BASE_DIR / "image_metadata.json"

for dir_path in [UPLOAD_DIR, CHUNKS_DIR, IMAGES_DIR]:
    dir_path.mkdir(exist_ok=True)

# ------------------- Load Image Metadata + Precompute Embeddings (LOCAL) -------------------
with open(IMAGE_METADATA_PATH, "r", encoding="utf-8") as f:
    IMAGE_METADATA = json.load(f)

# Pre-compute image embeddings LOCAL (no API)
image_texts = [
    f"{img['title']} {img['description']} {' '.join(img['keywords'])}"
    for img in IMAGE_METADATA
]

print("Generating image embeddings locally...")
IMAGE_EMBEDDINGS = embedder.encode(image_texts)  # Local embedding

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_relevant_image(answer_text: str):
    if len(answer_text) < 10:
        return None
    answer_emb = embedder.encode([answer_text])[0]  # Local
    similarities = [cosine_sim(answer_emb, img_emb) for img_emb in IMAGE_EMBEDDINGS]
    best_idx = int(np.argmax(similarities))
    if similarities[best_idx] > 0.35:  # Threshold
        return IMAGE_METADATA[best_idx]["filename"]
    return None

# ------------------- PDF Upload -------------------
@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF allowed")

    topic_id = str(uuid.uuid4())
    pdf_path = UPLOAD_DIR / f"{topic_id}.pdf"
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Extract text
    reader = PyPDF2.PdfReader(str(pdf_path))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    # Chunking
    words = text.split()
    chunks = [" ".join(words[i:i+500]) for i in range(0, len(words), 400)]  # overlap

    # Generate embeddings using LOCAL model
    print(f"Generating embeddings for {len(chunks)} chunks locally...")
    embeddings = embedder.encode(chunks)  # Local
    chunk_data = [
        {"chunk": chunk, "embedding": emb.tolist()}  # Convert to list for JSON
        for chunk, emb in zip(chunks, embeddings)
    ]

    # Save
    with open(CHUNKS_DIR / f"{topic_id}.json", "w", encoding="utf-8") as f:
        json.dump(chunk_data, f)

    return {"topicId": topic_id, "chunks": len(chunks)}


# ------------------- Chat Request Model -------------------
class ChatRequest(BaseModel):
    question: str
    topicId: str


# ------------------- Chat Endpoint -------------------
@app.post("/chat")
async def chat(req: ChatRequest):
    chunk_file = CHUNKS_DIR / f"{req.topicId}.json"
    if not chunk_file.exists():
        raise HTTPException(404, "Upload PDF first")

    with open(chunk_file) as f:
        chunks = json.load(f)

    # Question embedding LOCAL
    q_emb = embedder.encode([req.question])[0]  # Local

    # Retrieve top 3 chunks
    similarities = [cosine_sim(q_emb, np.array(c["embedding"])) for c in chunks]
    top_indices = np.argsort(similarities)[-3:][::-1]
    context = "\n\n".join([chunks[i]["chunk"] for i in top_indices])

    # Prompt
    prompt = f"""You are an expert tutor. Answer only using the given context.

Context:
{context}

Question: {req.question}
Answer:"""

    # Generate answer using Groq (super fast + free)
    completion = client.chat.completions.create(
       model="llama-3.3-70b-versatile",   # Latest free model, super fast
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=600
    )
    answer = completion.choices[0].message.content.strip()

    # Smart image retrieval based on ANSWER (local)
    image_filename = get_relevant_image(answer)

    return {
        "answer": answer,
        "image": f"/images/{image_filename}" if image_filename else None
    }


# ------------------- Serve Images -------------------
@app.get("/images/{filename}")
async def serve_image(filename: str):
    path = IMAGES_DIR / filename
    if path.exists():
        return FileResponse(path)
    raise HTTPException(404, "Image not found")