from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import numpy as np
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, models
from collections import Counter
import random
import time
import numpy

from prediction.embedding.embedding_manager import EmbeddingManager
from prediction.embedding.qdrant_manager import QdrantManager


class PredictionService:
    """
    Service for predicting train arrival times using historical data from Qdrant.
    """

    def __init__(self, qdrant_manager=None, embedding_manager=None):
        """
        Initialize the PredictionService with a QdrantManager instance.
        """
        self.qdrant_manager = qdrant_manager
        self.embedding_manager = embedding_manager

    def predict_arrival_time(
        self,
        current_station: str,
        destination_station: str = "LST",
        current_delay: int = 0,  # Current delay in minutes
    ) -> Dict[str, Any]:
        """
        Predict arrival time at destination station based on current station and delay information.

        Args:
            current_station: Current station code (e.g., NRW, DIS, SMK)
            destination_station: Destination station code (default LST)
            current_delay: Current delay in minutes (default 0)

        Returns:
            Dict with predicted arrival information
        """
        # Always use system time
        current_time = datetime.now().strftime("%H:%M")

        # Extract hour and day for embedding generation
        current_dt = datetime.now()
        hour_of_day = current_dt.hour
        # Get current day of week (0=Monday, 6=Sunday)
        day_of_week = current_dt.weekday()

        # Basic validation
        if self.qdrant_manager is None:
            return {"error": "QdrantManager instance is required"}

        try:
            search_vector = self.embedding_manager.create_search_vector(
                current_station, hour_of_day, day_of_week, current_delay
            )

            # Find similar journeys for the target segment
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="station", match=MatchValue(value=current_station)
                    )
                ]
            )

            # Query Qdrant for similar journeys
            similar_journeys = self.qdrant_manager.client.search(
                collection_name=self.qdrant_manager.collection_name,
                query_vector=search_vector,
                query_filter=filter_condition,
                limit=20,  # Top 20 similar journeys
            )

            if not similar_journeys:
                return {"error": "No similar journeys found"}

            # Collect train IDs from similar journeys
            train_ids = [journey.payload["rid"] for journey in similar_journeys]

            # Get dynamic route and journey times using similar trains
            sample_size = len(train_ids)
            all_routes = []
            all_journey_times = {}

            for i in range(sample_size):
                train_id = train_ids[i]
                route_segment, journey_times = self._extract_route_and_times(
                    train_id, current_station, destination_station
                )

                if route_segment:
                    all_routes.append(route_segment)

                    # Merge journey times
                    for segment, time in journey_times.items():
                        if segment not in all_journey_times:
                            all_journey_times[segment] = []
                        all_journey_times[segment].append(time)

            # Find the most common route
            if all_routes:
                # Convert routes to tuples for counting
                route_tuples = [tuple(route) for route in all_routes]
                most_common_route = Counter(route_tuples).most_common(1)[0][0]
                route = list(most_common_route)

                # Calculate average journey times
                avg_journey_times = {}
                for segment, times in all_journey_times.items():
                    avg_journey_times[segment] = sum(times) // len(times)

                journey_times = avg_journey_times
            else:
                # If no route found, use direct route from origin to destination
                route = [current_station, destination_station]
                journey_times = {}  # Will be handled with defaults in calculation

            # Create delay propagation model from current station to destination
            # Get delays for all similar trains instead of just the most similar one
            delays_by_station = self._get_delays_by_station(train_ids)

            delay_change_factor = self._calculate_delay_change_factor(
                delays_by_station, current_station, destination_station
            )

            # Calculate propagated delay
            propagated_delay = int(current_delay * delay_change_factor)

            # Calculate journey time from origin to destination using the route
            total_time = self._calculate_journey_time_from_route(route, journey_times)

            # Calculate expected arrival time
            journey_minutes = total_time + propagated_delay
            arrival_dt = current_dt + timedelta(minutes=journey_minutes)
            expected_arrival = arrival_dt.strftime("%H:%M")

            # Return results
            return {
                "origin": current_station,
                "destination": destination_station,
                "current_time": current_time,
                "current_delay": current_delay,
                "predicted_arrival_time": expected_arrival,
                "estimated_journey_time": total_time,
                "propagated_delay": propagated_delay,
                "route": route,  # Include the route used for prediction
            }

        except Exception as e:
            return {"error": str(e)}

    def _extract_route_and_times(
        self, train_id: str, origin: str, destination: str
    ) -> tuple:
        """
        Extract route segment and journey times between origin and destination for a specific train

        Args:
            train_id: The train ID to analyze
            origin: Origin station code
            destination: Destination station code

        Returns:
            Tuple containing (route_segment, journey_times)
        """
        try:
            # Get all stations for this train
            train_journey = self.qdrant_manager.client.scroll(
                collection_name=self.qdrant_manager.collection_name,
                scroll_filter=Filter(
                    must=[FieldCondition(key="rid", match=MatchValue(value=train_id))]
                ),
                with_payload=True,
                limit=50,  # Should be enough for all stops of a train
            )[0]

            if not train_journey:
                return [], {}

            # Sort by planned times to ensure proper order
            sorted_stops = sorted(
                train_journey,
                key=lambda x: (
                    x.payload.get("date", ""),
                    x.payload.get("planned_departure", "")
                    or x.payload.get("planned_arrival", "")
                    or "",
                ),
            )

            # Extract station sequence
            full_route = [stop.payload["station"] for stop in sorted_stops]

            # Find indices of origin and destination
            try:
                origin_idx = full_route.index(origin)
                dest_idx = full_route.index(destination)
            except ValueError:
                # Origin or destination not found in this train's route
                return [], {}

            # Extract the route segment
            if origin_idx < dest_idx:
                route_segment = full_route[origin_idx : dest_idx + 1]
            else:
                # If destination comes before origin in the sequence, return empty
                return [], {}

            # Extract journey times between stations
            journey_times = {}
            for i in range(len(route_segment) - 1):
                segment = f"{route_segment[i]}-{route_segment[i+1]}"

                # Try to calculate the time between these stations
                curr_station = sorted_stops[origin_idx + i].payload
                next_station = sorted_stops[origin_idx + i + 1].payload

                # Use departure from current and arrival at next when available
                curr_dep = curr_station.get("planned_departure", "")
                next_arr = next_station.get("planned_arrival", "")

                if curr_dep and next_arr:
                    # Calculate time difference in minutes
                    dep_time = datetime.strptime(curr_dep, "%H:%M")
                    arr_time = datetime.strptime(next_arr, "%H:%M")

                    # Handle overnight journeys (if arrival is earlier than departure)
                    if arr_time < dep_time:
                        arr_time = arr_time + timedelta(days=1)

                    time_diff = (arr_time - dep_time).seconds // 60
                    journey_times[segment] = time_diff
                else:
                    # Use default time if planned times not available
                    journey_times[segment] = 15

            return route_segment, journey_times

        except Exception as e:
            print(f"Error extracting route for train {train_id}: {e}")
            return [], {}

    def _get_delays_by_station(self, train_ids: List[str]) -> Dict[str, int]:
        """
        Get average delay information for each station visited by multiple trains

        Args:
            train_ids: List of train IDs to analyze

        Returns:
            Dictionary mapping station codes to average delay minutes
        """
        all_delays_by_station = (
            {}
        )  # Will collect delays for all stations across all trains
        station_count = {}  # Count how many trains have data for each station

        for train_id in train_ids:
            try:
                train_journey = self.qdrant_manager.client.scroll(
                    collection_name=self.qdrant_manager.collection_name,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(key="rid", match=MatchValue(value=train_id))
                        ]
                    ),
                    with_payload=["station", "delay_minutes"],
                    limit=50,  # Should be enough for all stops of a train
                )[0]

                for point in train_journey:
                    station_code = point.payload["station"]
                    delay = point.payload["delay_minutes"]

                    # Accumulate delays for each station
                    if station_code not in all_delays_by_station:
                        all_delays_by_station[station_code] = 0
                        station_count[station_code] = 0

                    all_delays_by_station[station_code] += delay
                    station_count[station_code] += 1

            except Exception as e:
                print(f"Error getting delays for train {train_id}: {e}")

        # Calculate average delays for each station
        avg_delays_by_station = {}
        for station, total_delay in all_delays_by_station.items():
            count = station_count[station]
            if count > 0:
                avg_delays_by_station[station] = total_delay / count
            else:
                avg_delays_by_station[station] = 0

        print("avg_delays_by_station", avg_delays_by_station)

        return avg_delays_by_station

    def _calculate_delay_change_factor(
        self,
        delays_by_station: Dict[str, int],
        current_station: str,
        destination_station: str,
    ) -> float:
        """
        Calculates delay change between stations based on learned patterns from real data
        """

        # Get all stations in route order
        all_stations = list(delays_by_station.keys())

        # Find indices of current and destination stations
        try:
            current_idx = all_stations.index(current_station)
            dest_idx = all_stations.index(destination_station)
        except ValueError:
            # Return default value if either station not found
            return 1.0

        # Analyze delay changes between stations from start to end
        if current_idx < dest_idx:
            # Get route segment between stations
            segment = all_stations[current_idx : dest_idx + 1]

            # Get delays at start and end of segment
            start_delay = delays_by_station.get(segment[0], 0)
            end_delay = delays_by_station.get(segment[-1], 0)

            print("delay change factor", end_delay / start_delay)

            # Use factor of 1 if no initial delay
            if start_delay == 0:
                return 1.0

            # Calculate actual change factor
            return end_delay / start_delay if start_delay > 0 else 1.0

        return 1.0  # Stations are in reverse order

    def _calculate_journey_time_from_route(
        self, route: List[str], journey_times: Dict[str, int]
    ) -> int:
        """
        Calculate total journey time based on a route and segment times

        Args:
            route: List of station codes in order
            journey_times: Dictionary mapping segments to journey times

        Returns:
            Total journey time in minutes
        """
        total_time = 0

        for i in range(len(route) - 1):
            segment = f"{route[i]}-{route[i+1]}"
            # Use journey_times if available, otherwise use default of 15 minutes
            segment_time = journey_times.get(segment, 15)
            total_time += segment_time

        return total_time


def get_prediction_service() -> PredictionService:
    """Get a prediction service"""
    embedding_manager = EmbeddingManager()

    embeddings = embedding_manager.generate_embeddings(
        [
            "data/service/2022_service_details.csv",
            "data/service/2023_service_details.csv",
            "data/service/2024_service_details.csv",
        ]
    )

    qdrant_manager = QdrantManager(embedding_dim=embedding_manager.embedding_dim)

    is_collection_exists = qdrant_manager.is_collection_exists()

    if not is_collection_exists:
        qdrant_manager.initialize_collection()
        qdrant_manager.upload_embeddings(embeddings)

    prediction_service = PredictionService(qdrant_manager, embedding_manager)

    return prediction_service

def get_test_prediction_service() -> PredictionService:
    """Get a prediction service for testing"""
    embedding_manager = EmbeddingManager()

    embeddings = embedding_manager.generate_embeddings(
        [
            "data/service/2022_service_details.csv",
            "data/service/2023_service_details.csv",
            "data/service/2024_service_details.csv",
        ]
    )

    qdrant_manager = QdrantManager(embedding_dim=embedding_manager.embedding_dim)

    is_collection_exists = qdrant_manager.is_collection_exists()

    dataset_iterator = iter(embeddings)
    testing_number = 10000
    print("There are " + str(len(embeddings)) + " embeddings overall.")
    testing_embeddings = [next(dataset_iterator) for _ in range(testing_number)]
    print("There are " + str(len(testing_embeddings)) + " embeddings for testing.")
    training_embeddings = [next(dataset_iterator) for _ in range(len(embeddings) - testing_number)]
#    training_embeddings = [next(dataset_iterator) for _ in range(10)]
    print("There are " + str(len(training_embeddings)) + " embeddings for training.")
    if not is_collection_exists:
        qdrant_manager.initialize_collection()
        qdrant_manager.upload_embeddings(training_embeddings)

    prediction_service = PredictionService(qdrant_manager, embedding_manager)

    def avg_precision_at_k(k: int):
        precisions = []
        for item in testing_embeddings:
#            print(item[1])
            ann_result = qdrant_manager.client.query_points(
                    collection_name=qdrant_manager.collection_name,
                    query=item[1],
                    limit=k,
                    ).points
            knn_result = qdrant_manager.client.query_points(
                    collection_name=qdrant_manager.collection_name,
                    query=item[1],
                    limit=k,
                    search_params=models.SearchParams(
                        exact=True,
                        ),
                    ).points
            ann_ids = set(item.id for item in ann_result)
            knn_ids = set(item.id for item in knn_result)
            precision = len(ann_ids.intersection(knn_ids)) / k
            precisions.append(precision)
    
        return sum(precisions) / len(precisions)

    def avg_cosine_and_dot_product_of_ann(k: int):

        cosine_precisions = []
        dot_precisions = []

        def apply_normalisation_factor(vector):
            sum_squares = 0.0
            for i in vector:
                sum_squares += pow(i, 2)
            return_list = []
            normalisation_factor = pow(sum_squares, 0.5)
            for i in vector:
                return_list.append(i/normalisation_factor)
            return(return_list)

        for item in testing_embeddings:
#            print(item[1])
            ann_result = qdrant_manager.client.search(
                    collection_name=qdrant_manager.collection_name,
                    query_vector=item[1],
                    limit=k,
                    with_vectors=True,
                    )
            vec_a = apply_normalisation_factor(item[1])
            vec_b = apply_normalisation_factor(ann_result[0].vector)
            cosine_precision = numpy.dot(item[1], ann_result[0].vector)/(numpy.linalg.norm(item[1])* numpy.linalg.norm(ann_result[0].vector))
            dot_precision = numpy.dot(vec_a, vec_b, out = None)
#            print(item[1])
#            print(ann_result[0].vector)
            dot_precisions.append(dot_precision)
            cosine_precisions.append(cosine_precision)
        return (sum(cosine_precisions) / len(cosine_precisions)), (sum(dot_precisions) / len(dot_precisions))
#            return 0

    start_time = time.time()
    print("Ann accuracy: " + str(avg_precision_at_k(1)))
    cosine_avg, dot_product_avg = avg_cosine_and_dot_product_of_ann(1)
    print("Cosine accuracy: " + str(cosine_avg))
    print("Normalised dot product accuracy: " + str(dot_product_avg))
    end_time = time.time()
    print("In " + str(end_time - start_time) + " seconds.")

    return prediction_service
