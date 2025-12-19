from flask import Blueprint, request, jsonify
from backend.application.gas_station_service import GasStationService
from backend.domain.models import LatType, LonType, DistanceType
from backend.infraestructure.gob_gas_stations_repository import GasStationsRepository
from backend.infraestructure.math_distance_repository import DistanceRepository

gs = Blueprint("gs", __name__)

gas_station_service = GasStationService(
    GasStationsRepository(),
    DistanceRepository(),
)


@gs.route("/refresh")  # type: ignore
def refresh():
    global gas_station_service
    gas_station_service.refresh_data()
    return jsonify(gas_station_service.collect_json(None))  # type: ignore


@gs.get("/<int:num_of_results>")  # type: ignore
def get_stations(num_of_results: int | None = None) -> str:
    global gas_station_service
    petrol_type: str | None = request.args.get("petrol", type=str)
    ccaa: str | None = request.args.get("ccaa", type=str)
    distance: DistanceType | None = request.args.get("distance", type=DistanceType)
    lat: LatType | None = request.args.get("lat", type=LatType)
    lon: LonType | None = request.args.get("lon", type=LonType)

    gas_station_service.get_stations().filter_by_ccaa(ccaa).filter_by_distance(
        distance, lat, lon
    ).sort_by_price(petrol_type)

    # type: ignore
    return jsonify(gas_station_service.collect_json(num_of_results))
