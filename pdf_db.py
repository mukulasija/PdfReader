import sqlite3
from datetime import datetime
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import torch
import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader

class ConversationDB:
    def __init__(self, pdf_name="ConversationDb", db_name = "ConversationDb", embedding_model="all-MiniLM-L6-v2"):
        print(f"Initializing with PDF: {pdf_name}.pdf")
        self.pdf_name = pdf_name
        self.db_name = db_name
        self.embedding_model = SentenceTransformer(embedding_model)
        self.init_db()
        pdf_name = pdf_name + ".pdf"

        if self.pdf_already_stored(pdf_name):
            print(f"PDF '{pdf_name}' already exists. Deleting old entries...")
            self.delete_pdf_data(pdf_name)

        chunks = self.get_pdf_chunks(pdf_name)
        print(f"Chunks extracted: {len(chunks)}")
        self.init_faiss_index()  # Clear and reload FAISS

        for chunk in chunks:
            self.store_conversation(chunk, pdf_name=pdf_name)

    def delete_pdf_data(self, pdf_name):
        """Delete all conversation chunks related to a specific PDF."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM conversations WHERE pdf_name = ?', (pdf_name,))
        conn.commit()
        conn.close()

        # Also reset FAISS index and stored_ids
        self.index = None
        self.stored_ids = []

    def pdf_already_stored(self, pdf_name):
        """Check if this PDF's content already exists in the DB."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM conversations WHERE pdf_name = ?', (pdf_name,))
        count = cursor.fetchone()[0]
        print(count)
        conn.close()
        return count > 0


    def init_db(self):
        print(f"Initializing SQLite DB: {self.db_name}")
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pdf_name TEXT NOT NULL,
                chunk_text TEXT NOT NULL,
                message_embedding BLOB
            )
        ''')
        conn.commit()
        conn.close()

    def get_pdf_chunks(self, pdf_path: str, chunk_size: int = 300, chunk_overlap: int = 50) -> list:
        try:
            print(f"Reading and chunking PDF: {pdf_path}")
            reader = PdfReader(pdf_path)
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() or ""
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = splitter.split_text(full_text)
        return chunks

    def init_faiss_index(self, pdf_name=None):
        """Initialize or load FAISS index for semantic search."""
        print(f"Initializing FAISS index for: {pdf_name or 'all PDFs'}")
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        if pdf_name:
            cursor.execute('''
                SELECT id, message_embedding FROM conversations
                WHERE pdf_name = ? AND message_embedding IS NOT NULL
            ''', (pdf_name,))
        else:
            cursor.execute('''
                SELECT id, message_embedding FROM conversations
                WHERE message_embedding IS NOT NULL
            ''')
        results = cursor.fetchall()

        embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.stored_ids = []

        if results:
            embeddings = []
            for id_, emb_blob in results:
                embedding = np.frombuffer(emb_blob, dtype=np.float32)
                embeddings.append(embedding)
                self.stored_ids.append(id_)

            embeddings_array = np.vstack(embeddings)
            self.index.add(embeddings_array)

        conn.close()

    def compute_embedding(self, text):
        embedding = self.embedding_model.encode(text, convert_to_tensor=True)
        return embedding.cpu().numpy().astype(np.float32)

    def store_conversation(self, chunk_text, pdf_name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        embedding = self.compute_embedding(chunk_text)
        embedding_blob = embedding.tobytes()

        cursor.execute('''
            INSERT INTO conversations (pdf_name, chunk_text, message_embedding)
            VALUES (?, ?, ?)
        ''', (pdf_name, chunk_text, embedding_blob))

        self.index.add(embedding.reshape(1, -1))
        self.stored_ids.append(cursor.lastrowid)

        conn.commit()
        conn.close()

    def get_similar_conversations(self, query_text, k=3, pdf_name=None):
        query_embedding = self.compute_embedding(query_text)

        if len(self.stored_ids) == 0:
            return []

        distances, indices = self.index.search(query_embedding.reshape(1, -1), min(k, len(self.stored_ids)))

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        similar_conversations = []

        for idx, distance in zip(indices[0], distances[0]):
            if idx >= 0:
                conversation_id = self.stored_ids[idx]

                if pdf_name:
                    cursor.execute('''
                        SELECT chunk_text FROM conversations
                        WHERE id = ? AND pdf_name = ?
                    ''', (conversation_id, pdf_name))
                else:
                    cursor.execute('''
                        SELECT chunk_text FROM conversations
                        WHERE id = ?
                    ''', (conversation_id,))
                result = cursor.fetchone()
                if result:
                    similarity_score = 1 / (1 + distance)
                    similar_conversations.append({
                        'chunk_text': result[0]
                    })

        conn.close()
        return similar_conversations
