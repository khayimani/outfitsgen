import os
from pinecone import Pinecone, ServerlessSpec

class PineconeService:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY", "mock-key")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "wardrobe-index")
        self.dimension = 512
        
        # Initialize Pinecone
        try:
            self.pc = Pinecone(api_key=self.api_key)
            # Check if index exists, if not create it (if we have permissions/real key)
            # For now, we assume it exists or we handle errors
            self.index = self.pc.Index(self.index_name)
        except Exception as e:
            print(f"Pinecone init error (expected if mock): {e}")
            self.index = None

    def upsert_vector(self, vector_id, vector, metadata=None):
        if not self.index:
            print(f"Mock upsert: {vector_id}")
            return True
        try:
            self.index.upsert(vectors=[(vector_id, vector, metadata)])
            return True
        except Exception as e:
            print(f"Error upserting to Pinecone: {e}")
            return False

    def search(self, vector, top_k=5):
        if not self.index:
            print("Mock search")
            return []
        try:
            results = self.index.query(vector=vector, top_k=top_k, include_metadata=True)
            return results
        except Exception as e:
            print(f"Error searching Pinecone: {e}")
            return []

pinecone_service = PineconeService()
