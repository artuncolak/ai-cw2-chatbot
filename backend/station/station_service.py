"""
Service for retrieving and managing station data
"""

from typing import Optional, List
from sqlmodel import select

from api.database.models import Station
from api.database.connection import get_session


class StationService:
    """
    Service for retrieving station data from the database
    """

    @staticmethod
    def get_by_code(code: str) -> Optional[Station]:
        """
        Get a station by its code

        Args:
            code: The station code to search for

        Returns:
            Station object if found, None otherwise
        """
        session = next(get_session())
        try:
            statement = select(Station).where(Station.code == code)
            result = session.exec(statement).first()
            return result
        finally:
            session.close()

    @staticmethod
    def search_by_name(name: str, limit: int = 10) -> List[Station]:
        """
        Search for stations by name (partial match)

        Args:
            name: The partial name to search for
            limit: Maximum number of results to return

        Returns:
            List of matching Station objects
        """
        session = next(get_session())
        try:
            # Using ILIKE for case-insensitive search with PostgreSQL
            # The % wildcards allow for partial matches
            statement = (
                select(Station).where(Station.name.ilike(f"%{name}%")).limit(limit)
            )

            result = session.exec(statement).all()
            return result
        finally:
            session.close()

    @staticmethod
    def get_all() -> List[Station]:
        """
        Get all stations

        Returns:
            List of all Station objects
        """
        session = next(get_session())
        try:
            statement = select(Station)
            result = session.exec(statement).all()
            return result
        finally:
            session.close()
