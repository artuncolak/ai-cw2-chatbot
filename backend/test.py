from station import StationService
#from .station import StationService

london_station = StationService.get_by_code("LDN")
if london_station:
    print(f"Found: {london_station.name} ({london_station.code})")
