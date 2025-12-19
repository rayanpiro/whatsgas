from backend.domain.repository_interface import IGasStationsRepository
from backend.domain.models import GasStation, PetrolType, Gas95E5, Gas95E5Premium, Gas95E10, Gas98E5, Gas98E10, GasOilA, GasOilAPremium
import requests

ccaa_dict = {
    "01" : "Andalucia",
    "02" : "Aragón",
    "03" : "Asturias",
    "04" : "Baleares",
    "05" : "Canarias",
    "06" : "Cantabria",
    "07" : "Castilla la Mancha",
    "08" : "Castilla y León",
    "09" : "Cataluña",
    "10" : "Comunidad Valenciana",
    "11" : "Extremadura",
    "12" : "Galicia",
    "13" : "Madrid",
    "14" : "Murcia",
    "15" : "Navarra",
    "16" : "País Vasco",
    "17" : "La Rioja",
    "18" : "Ceuta",
    "19" : "Melilla",
}

# petrol_types = {
#     Gas95E5: "01",
#     Gas95E10: "23",
#     Gas95E5Premium: "20",
#     Gas98E5: "03",
#     Gas98E10: "21",
#     GasOilA: "04",
#     GasOilAPremium: "05",
# }

def str2float(x: str) -> float:
    return float(x.replace(",", "."))

def parseCoords(x: dict[str, str]) -> tuple[float, float]:
    return ( str2float(x["Latitud"]), str2float(x["Longitud (WGS84)"]) )

from typing import Type
def parsePetrolTypes(x: dict[str, str]) -> dict[Type[PetrolType], PetrolType]:

    petrol_api_keys = {
        'Precio Gasoleo A': GasOilA,
        'Precio Gasoleo Premium': GasOilAPremium,
        'Precio Gasolina 95 E10': Gas95E10,
        'Precio Gasolina 95 E5': Gas95E5,
        'Precio Gasolina 95 E5 Premium': Gas95E5Premium,
        'Precio Gasolina 98 E10': Gas98E10,
        'Precio Gasolina 98 E5': Gas98E5,
    }

    ret_dict: dict[Type[PetrolType], PetrolType] = {}
    for key, value in petrol_api_keys.items():
        if x[key] != '':
            ret_dict[value] = value(str2float(x[key]))

    return ret_dict

class GasStationsRepository(IGasStationsRepository):
    def __init__(self):
        self._api_location = 'https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/'
    
    def __parse_response(self, repo_response) -> list[GasStation]:
        return list(
            map(lambda x: GasStation(
                    x["Rótulo"],
                    x["Dirección"]+", "+x["Provincia"],
                    ccaa_dict[x["IDCCAA"]],
                    parseCoords(x), x["Horario"],
                    parsePetrolTypes(x)
                ),
                repo_response
            )
        )

    def fetch_data(self) -> list[GasStation]:
        res = requests.get(self._api_location, verify=False)

        public_stations: list[dict[str, str]] = list(filter(lambda x: x['Tipo Venta'] == 'P', res.json()["ListaEESSPrecio"]))

        self._cache = public_stations
        return self.__parse_response(self._cache)
    
    def get_cached(self) -> list[GasStation]:
        return self.__parse_response(self._cache)
