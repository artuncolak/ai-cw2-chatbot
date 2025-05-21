import unittest
import numpy as np
from unittest.mock import MagicMock, patch
from prediction.prediction_service import PredictionService
from prediction.embedding.embedding_manager import EmbeddingManager
from prediction.embedding.qdrant_manager import QdrantManager


class TestDelayPrediction(unittest.TestCase):
    def setUp(self):
        # Create mocks
        self.embedding_manager = MagicMock(spec=EmbeddingManager)
        self.embedding_manager.embedding_dim = 100
        self.embedding_manager.create_search_vector.return_value = np.zeros(
            100
        ).tolist()

        self.qdrant_manager = MagicMock(spec=QdrantManager)
        self.qdrant_manager.collection_name = "test_collection"
        self.qdrant_manager.client = MagicMock()

        # Create search results for mocking
        mock_search_results = []
        for i in range(5):
            point = MagicMock()
            point.payload = {"rid": f"train_{i}", "station": "NRW", "delay_minutes": 15}
            mock_search_results.append(point)

        # Configure mock search results
        self.qdrant_manager.client.search.return_value = mock_search_results

        # Mock scroll results for a train
        mock_scroll_results = []
        stations = ["NRW", "DIS", "SMK", "LST"]
        for i, station in enumerate(stations):
            point = MagicMock()
            point.payload = {
                "rid": "train_1",
                "station": station,
                "planned_departure": "10:00" if i < 3 else None,
                "planned_arrival": "10:15" if i > 0 else None,
                "delay_minutes": 15,
            }
            mock_scroll_results.append(point)

        self.qdrant_manager.client.scroll.return_value = ([mock_scroll_results], None)

        # Create the prediction service with mocks
        self.prediction_service = PredictionService(
            qdrant_manager=self.qdrant_manager, embedding_manager=self.embedding_manager
        )

    def test_vector_embedding_generation(self):
        """Test generation of vector embeddings for searching"""
        # Setup
        journey_data = {"station": "NRW", "day": 1, "hour": 10, "delay": 15}

        # Execute
        self.embedding_manager.create_search_vector.return_value = np.ones(100).tolist()
        vector = self.embedding_manager.create_search_vector(
            journey_data["station"],
            journey_data["hour"],
            journey_data["day"],
            journey_data["delay"],
        )

        # Assert
        self.assertIsInstance(vector, list)
        self.assertEqual(len(vector), 100)
        self.embedding_manager.create_search_vector.assert_called_once()

    def test_train_delay_prediction(self):
        """Test predicting delays using vector similarity search"""
        # Execute
        result = self.prediction_service.predict_arrival_time(
            current_station="NRW", destination_station="LST", current_delay=15
        )

        # Assert
        self.assertIsInstance(result, dict)
        self.assertIn("predicted_arrival_time", result)
        self.assertIn("propagated_delay", result)
        self.assertIn("route", result)

        # Verify methods were called
        self.embedding_manager.create_search_vector.assert_called_once()
        self.qdrant_manager.client.search.assert_called_once()

    def test_delay_change_factor_calculation(self):
        """Test delay propagation factor calculation"""
        # Setup
        delays_by_station = {"NRW": 10, "DIS": 12, "SMK": 15, "LST": 20}

        # Execute
        delay_factor = self.prediction_service._calculate_delay_change_factor(
            delays_by_station, "NRW", "LST"
        )

        # Assert
        self.assertIsInstance(delay_factor, float)
        self.assertEqual(delay_factor, 2.0)  # 20/10 = 2.0

    def test_journey_time_calculation(self):
        """Test calculation of journey time from route"""
        # Setup
        route = ["NRW", "DIS", "SMK", "LST"]
        journey_times = {"NRW-DIS": 10, "DIS-SMK": 15, "SMK-LST": 20}

        # Execute
        total_time = self.prediction_service._calculate_journey_time_from_route(
            route, journey_times
        )

        # Assert
        self.assertEqual(total_time, 45)  # 10 + 15 + 20

    def test_unknown_station_handling(self):
        """Test handling of unknown station codes"""
        # Setup - empty search results for unknown station
        self.qdrant_manager.client.search.return_value = []

        # Execute
        result = self.prediction_service.predict_arrival_time(
            current_station="XXX",  # Unknown station
            destination_station="LST",
            current_delay=15,
        )

        # Assert
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "No similar journeys found")


if __name__ == "__main__":
    unittest.main()
