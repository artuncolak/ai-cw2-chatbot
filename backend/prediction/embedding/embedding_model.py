from datetime import datetime
from typing import Optional
import pandas as pd


class EmbeddingModel:
    """
    Represents a train delay data point with structured fields.
    This class is a representation of train journey data with focus on delay information.
    """

    def __init__(
        self,
        rid: str,
        station: str,
        date: str,
        planned_departure: Optional[str] = None,
        actual_departure: Optional[str] = None,
        planned_arrival: Optional[str] = None,
        actual_arrival: Optional[str] = None,
    ):
        """
        Initialize a new EmbeddingModel instance.

        Args:
            rid: Train ID
            station: Station code (e.g., NRW, LST)
            date: Service date in format DD/MM/YYYY
            planned_departure: Planned departure time (HH:MM)
            actual_departure: Actual departure time (HH:MM)
            planned_arrival: Planned arrival time (HH:MM)
            actual_arrival: Actual arrival time (HH:MM)
        """
        self.rid = rid
        self.station = station
        self.date = date
        self.planned_departure = planned_departure
        self.actual_departure = actual_departure
        self.planned_arrival = planned_arrival
        self.actual_arrival = actual_arrival

        # Calculate delay automatically
        self.delay_minutes = max(
            self._calculate_delay(planned_arrival, actual_arrival),
            self._calculate_delay(planned_departure, actual_departure),
            0
        )

        # Derived fields
        self.day_of_week = self._calculate_day_of_week()
        self.hour_of_day = self._calculate_hour_of_day()
        self.time_category = self._determine_time_category()

    def _calculate_day_of_week(self) -> Optional[int]:
        """Calculate day of week from the date (0=Monday, 6=Sunday)"""
        if not self.date:
            return None

        try:
            date_obj = datetime.strptime(self.date, "%d/%m/%Y")
            return date_obj.weekday()
        except ValueError:
            return None

    def _calculate_hour_of_day(self) -> Optional[int]:
        """Extract hour from planned departure or arrival time"""
        time_str = self.planned_departure or self.planned_arrival
        if not time_str:
            return None

        try:
            time_obj = datetime.strptime(time_str, "%H:%M")
            return time_obj.hour
        except ValueError:
            return None

    def _determine_time_category(self) -> Optional[str]:
        """Categorize the time as morning, afternoon, or evening"""
        hour = self._calculate_hour_of_day()
        if hour is None:
            return None

        if hour < 12:
            return "morning"
        elif hour < 18:
            return "afternoon"
        else:
            return "evening"

    def _calculate_delay(
        self, planned_time: Optional[str], actual_time: Optional[str]
    ) -> int:
        """Calculate delay in minutes between planned and actual times"""
        if not planned_time or not actual_time:
            return 0

        try:
            planned = datetime.strptime(planned_time, "%H:%M")
            actual = datetime.strptime(actual_time, "%H:%M")

            # Calculate difference in minutes
            delta_hours = actual.hour - planned.hour
            delta_minutes = actual.minute - planned.minute

            total_minutes = delta_hours * 60 + delta_minutes

            # Handle edge cases with negative time
            if total_minutes < -60:  # Likely an error
                return 0
            if total_minutes < 0:  # Small negative might be rounding error
                return 0

            return total_minutes
        except ValueError:
            return 0

    def __str__(self) -> str:
        """String representation of the model showing train details and timing information"""
        # Build timing info string
        timing_info = []
        if self.planned_departure and self.actual_departure:
            departure_delay = self._calculate_delay(
                self.planned_departure, self.actual_departure
            )
            timing_info.append(
                f"departed {self.actual_departure} (planned {self.planned_departure}, delay {departure_delay}m)"
            )
        if self.planned_arrival and self.actual_arrival:
            arrival_delay = self._calculate_delay(
                self.planned_arrival, self.actual_arrival
            )
            timing_info.append(
                f"arrived {self.actual_arrival} (planned {self.planned_arrival}, delay {arrival_delay}m)"
            )
        timing_str = ", ".join(timing_info)

        # Add delay info if delayed
        delay_info = ""
        if self.delay_minutes > 0:
            delay_info = f", delayed by {self.delay_minutes} minutes"

        # Build full string
        base = f"Train {self.rid} at {self.station} on {self.date}"
        if timing_str:
            base += f" - {timing_str}"
        base += delay_info

        return base
