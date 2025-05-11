from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct, Distance, VectorParams
from .embedding_model import EmbeddingModel


class QdrantManager:
    """
    A class to manage interactions with the Qdrant vector database.
    This handles uploading and searching embeddings.
    """

    def __init__(
        self,
        embedding_dim: int,
        collection_name: str = "train_delays",
        host: str = "qdrant.orb.local",
        port: int = 6333,
    ):
        """
        Initialize the QdrantManager

        Args:
            collection_name: Name of the Qdrant collection
            host: Qdrant server host
            port: Qdrant server port
        """
        self.collection_name = collection_name
        self.host = host
        self.port = port
        self.client = QdrantClient(host=host, port=port)
        self.embedding_dim = embedding_dim

    def initialize_collection(self) -> bool:
        """
        Create a new collection in Qdrant if it doesn't exist

        Args:
            embedding_dim: Dimension of the vector embeddings

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name in collection_names:
                print(f"Collection '{self.collection_name}' already exists")
                return True

            # Create new collection with specified parameters
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim, distance=Distance.COSINE
                ),
            )

            print(
                f"Created collection '{self.collection_name}' with dimension {self.embedding_dim}"
            )
            return True

        except Exception as e:
            print(f"Error initializing collection: {e}")
            return False

    def upload_embeddings(
        self,
        embeddings: list[Tuple[str, np.ndarray, Dict[str, Any]]],
        batch_size: int = 100,
    ) -> bool:
        """
        Upload embeddings to Qdrant

        Args:
            embeddings: List of tuples (id, vector, payload)
            embedding_dim: Dimension of the embeddings
            batch_size: Number of embeddings to upload in each batch

        Returns:
            True if successful, False otherwise
        """
        try:
            if not embeddings:
                print("No embeddings to upload")
                return False

            # Convert embeddings to Qdrant format
            points = []
            for point_id, vector, payload in embeddings:
                point = PointStruct(id=point_id, vector=vector, payload=payload)
                points.append(point)

            # Upload in batches
            total_uploaded = 0
            for i in range(0, len(points), batch_size):
                batch = points[i : i + batch_size]
                self.client.upsert(collection_name=self.collection_name, points=batch)
                total_uploaded += len(batch)
                print(f"Uploaded {total_uploaded}/{len(points)} embeddings")

            print(
                f"Successfully uploaded {total_uploaded} embeddings to collection '{self.collection_name}'"
            )
            return True

        except Exception as e:
            print(f"Error uploading embeddings: {e}")
            return False

    def get_collection_info(self) -> Dict:
        """
        Get information about the collection

        Returns:
            Dictionary with collection information
        """
        try:
            collections = self.client.get_collections().collections
            for collection in collections:
                if collection.name == self.collection_name:
                    return {
                        "name": collection.name,
                        "vectors_count": collection.vectors_count,
                        "status": str(collection.status),
                    }

            return {"error": f"Collection '{self.collection_name}' not found"}

        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {"error": str(e)}

    def delete_collection(self) -> bool:
        """
        Delete the collection from Qdrant

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            print(f"Deleted collection '{self.collection_name}'")
            return True

        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False
