from prediction import EmbeddingManager, QdrantManager, PredictionService

"""Main"""

import uvicorn
from api import create_app

app = create_app()


def main():
    """Run the application."""
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

    # embedding_manager = EmbeddingManager()

    # embeddings = embedding_manager.generate_embeddings(
    #     [
    #         "data/service/2022_service_details.csv",
    #         "data/service/2023_service_details.csv",
    #         "data/service/2024_service_details.csv",
    #     ]
    # )

    # qdrant_manager = QdrantManager(embedding_dim=embedding_manager.embedding_dim)
    # qdrant_manager.initialize_collection()
    # qdrant_manager.upload_embeddings(embeddings)

    # prediction_service = PredictionService(
    #     qdrant_manager=qdrant_manager, embedding_manager=embedding_manager
    # )

    # result = prediction_service.predict_arrival_time(
    #     current_station="IPS", destination_station="LST", current_delay=9
    # )
    # print(result)

    # print(embeddings)


if __name__ == "__main__":
    main()
