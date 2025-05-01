#!/usr/bin/env python3
"""
Wrapper script to test the stations service from the root directory
"""
import sys
from station.test_station_service import test_station_service

if __name__ == "__main__":
    print("Testing the StationService...")
    test_station_service() 