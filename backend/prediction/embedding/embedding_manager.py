import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from .embedding_model import EmbeddingModel


class EmbeddingManager:
    """
    A class that reads CSV files and produces EmbeddingModel objects.
    """

    embedding_models: List[EmbeddingModel] = []
    vector_embeddings: List[Tuple[str, np.ndarray, Dict[str, Any]]] = []

    def __init__(self):
        """EmbeddingManager class initializer"""
        self.preprocessor = None
        self.categorical_values = {
            "station": [],
            "hour": list(range(24)),  # 0-23 hours
            "day": list(range(7)),  # 0-6 days of week
        }
        self.embedding_dim = 0  # Will be set after preprocessor is initialized

    def create_search_vector(self, station: str, hour: int, day: int, delay: int) -> List[float]:
        """
        Create a search vector for querying similar train journeys
        
        Args:
            station: Station code (e.g., NRW, DIS)
            hour: Hour of day (0-23)
            day: Day of week (0-6, Monday=0)
            delay: Current delay in minutes
            
        Returns:
            List of floats representing the embedding vector
        """
        if self.preprocessor is None:
            raise ValueError("Preprocessor not initialized. Call generate_embeddings first.")
            
        # Create a feature dictionary similar to what we use for training
        features = {
            "station": station,
            "delay_minutes": float(delay),
            "hour": hour,
            "day": day,
            "has_departure": 1.0 if station != "NRW" else 0.0, 
            "has_arrival": 1.0,  
        }
        
        # Convert to DataFrame (required by the preprocessor)
        df = pd.DataFrame([features])
        
        try:
            # Apply the same preprocessing as during training
            vector = self.preprocessor.transform(df)
            
            # Convert to dense array if sparse
            if hasattr(vector, "toarray"):
                vector = vector.toarray()
                
            # Return as flat list
            return vector[0].tolist()
        except Exception as e:
            print(f"Error creating search vector: {e}")
            # Fallback: return zero vector of correct dimension
            return [0.0] * self.embedding_dim

    def _read_row_data(self, row: dict, key: str, default: str = "") -> str:
        """Read row data and return a string representation"""
        value = (
            str(row.get(key, default))
            if row.get(key) is not None and not pd.isna(row.get(key))
            else default
        )
        return value

    def _read_csv_files(self, csv_paths: List[str]) -> List[dict]:
        """Read CSV files and return a list of dictionaries"""
        all_rows = []
        total_rows = 0

        for csv_path in csv_paths:
            print(f"Reading CSV file: {csv_path}")
            try:
                # Read the CSV
                df = pd.read_csv(csv_path)
                file_rows = len(df)
                total_rows += file_rows
                print(f"Number of rows: {file_rows}")

                # Convert DataFrame to a list of dictionaries
                rows = df.to_dict("records")
                all_rows.extend(rows)
                print(f"Processed file: {csv_path}")
            except Exception as e:
                print(f"CSV reading error ({csv_path}): {e}")

        return all_rows

    def generate_embedding_model(self, row: dict) -> Optional[EmbeddingModel]:
        """
        Generate an EmbeddingModel object from a row of data

        Args:
            row: Dictionary containing train data

        Returns:
            EmbeddingModel instance or None if error occurs
        """
        try:
            # Now create the model with all properly formatted fields
            return EmbeddingModel(
                rid=self._read_row_data(row, "rid"),
                station=self._read_row_data(row, "location"),
                date=self._read_row_data(row, "date_of_service"),
                planned_departure=self._read_row_data(
                    row, "planned_departure_time", None
                ),
                actual_departure=self._read_row_data(
                    row, "actual_departure_time", None
                ),
                planned_arrival=self._read_row_data(row, "planned_arrival_time", None),
                actual_arrival=self._read_row_data(row, "actual_arrival_time", None),
            )
        except Exception as e:
            print(f"Error creating EmbeddingModel: {e}, values: {row}")
            return None

    def generate_embeddings(self, csv_paths: List[str]):
        """
        Reads CSV files and converts data to EmbeddingModel objects

        Args:
            csv_paths: List of CSV file paths
        """
        all_models = []

        rows = self._read_csv_files(csv_paths)
        for row in rows:
            model = self.generate_embedding_model(row)
            if model:
                all_models.append(model)

        print(f"Total {len(rows)} rows processed.")
        print(f"Total models created: {len(all_models)}")

        # Collect all station codes for categorical encoding
        self.categorical_values["station"] = list(
            set([model.station for model in all_models if model.station])
        )
        print(f"Station codes: {self.categorical_values['station']}")

        self.embedding_models = all_models

        return self.create_vector_embeddings()

    def _extract_features(self, model: EmbeddingModel) -> Dict[str, Any]:
        """
        Extract model features for embedding generation

        Args:
            model: EmbeddingModel instance

        Returns:
            Dictionary of features
        """
        # Basic features
        has_departure = 1 if model.planned_departure and model.actual_departure else 0
        has_arrival = 1 if model.planned_arrival and model.actual_arrival else 0

        # Get features that might be None
        hour = model.hour_of_day if model.hour_of_day is not None else 0
        day = model.day_of_week if model.day_of_week is not None else 0

        return {
            "station": model.station,
            "delay_minutes": float(model.delay_minutes),
            "hour": hour,
            "day": day,
            "has_departure": float(has_departure),
            "has_arrival": float(has_arrival),
        }

    def _initialize_preprocessor(self, sample_features: List[Dict[str, Any]]):
        """
        Initialize the feature preprocessing pipeline

        Args:
            sample_features: List of feature dictionaries to initialize the preprocessor
        """
        print("Initializing feature preprocessor...")

        # Define numeric and categorical features
        numeric_features = ["delay_minutes", "has_departure", "has_arrival"]
        categorical_features = ["station", "hour", "day"]

        # Create transformers
        numeric_transformer = StandardScaler()
        categorical_transformer = OneHotEncoder(
            categories=[
                self.categorical_values["station"],
                self.categorical_values["hour"],
                self.categorical_values["day"],
            ],
            handle_unknown="ignore",
        )

        # Create column transformer
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, numeric_features),
                ("cat", categorical_transformer, categorical_features),
            ],
            remainder="drop",  # Drop non-specified columns
        )

        # Create and fit the pipeline
        self.preprocessor = Pipeline(steps=[("preprocessor", preprocessor)])

        # Convert sample features to DataFrame
        df = pd.DataFrame(sample_features)

        # Fit the preprocessor
        self.preprocessor.fit(df)

        # Calculate embedding dimension
        self.embedding_dim = 0
        # Numeric features (scaled but dimension unchanged)
        self.embedding_dim += len(numeric_features)
        # Categorical features (one-hot encoded)
        self.embedding_dim += len(self.categorical_values["station"])
        self.embedding_dim += len(self.categorical_values["hour"])
        self.embedding_dim += len(self.categorical_values["day"])

        print(f"Preprocessor initialized. Embedding dimension: {self.embedding_dim}")

    def create_vector_embeddings(self):
        """
        Create vector embeddings for all EmbeddingModel instances
        """
        if not self.embedding_models:
            print("No embedding models to process. Call generate_embeddings first.")
            return

        print(f"Creating vector embeddings for {len(self.embedding_models)} models...")

        # Extract features from all models
        all_features = [
            self._extract_features(model) for model in self.embedding_models
        ]

        # Initialize preprocessor if not already initialized
        if self.preprocessor is None:
            self._initialize_preprocessor(all_features)

        # Convert features to DataFrame
        features_df = pd.DataFrame(all_features)

        # Generate embeddings using preprocessor
        embeddings = self.preprocessor.transform(features_df)

        # Convert to dense numpy arrays if sparse
        if hasattr(embeddings, "toarray"):
            embeddings = embeddings.toarray()

        # Store embeddings with metadata
        vector_embeddings = []
        for i, model in enumerate(self.embedding_models):
            # Create numeric ID - Qdrant requires integer or UUID
            # Here we use a simple incrementing integer
            point_id = i

            # Extract embedding vector
            vector = embeddings[i].tolist()

            # Create payload
            payload = {
                "rid": model.rid,
                "station": model.station,
                "date": model.date,
                "planned_departure": model.planned_departure,
                "actual_departure": model.actual_departure,
                "planned_arrival": model.planned_arrival,
                "actual_arrival": model.actual_arrival,
                "delay_minutes": model.delay_minutes,
                "day_of_week": model.day_of_week,
                "hour_of_day": model.hour_of_day,
                "time_category": model.time_category,
            }

            vector_embeddings.append((point_id, vector, payload))

        print(f"Created {len(vector_embeddings)} vector embeddings")
        return vector_embeddings
