import pandas as pd
import requests
from urllib.parse import urljoin



'''
TIMESTAMP/Index parameters
-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^
Filter
"410- Power consumption: Total (grid load)"
"4067- Power generation: Onshore wind"
"4068- Electricity generation: Photovoltaics"
"4169- Market price: Germany/Luxembourg"
-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^
region
DE- Country: Germany
AT- Country: Austria
LU- Country: Luxembourg
DE-LU- Market area: DE/LU (from October 1st, 2018)
DE-AT-LU- Market area: DE/AT/LU (until September 30, 2018)
50Hertz- Control area (DE): 50Hertz
Amprion- Control area (DE): Amprion
TenneT- Control area (DE): TenneT
TransnetBW- Control area (DE): TransnetBW
APG- Control area (AT): APG
Creos- Control area (LU): Creos
-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^-^
'''
BASE_URL="https://www.smard.de/app/"
endpoints={
    "TIMESTAMPS":"chart-data/{filter}/{region}/index_hour.json",
    "TIME_SERIES_CHART":"chart-data/{filter}/{region}/{filterCopy}_{regionCopy}_hour_{timestamp}.json",
    "TIME_SERIES_TABLE":"table-data/{filter}/{region}/{filterCopy}_{regionCopy}_quarterhour_{timestamp}.json",
}


def callEndPoints():


    filters={
        "LOAD_DE":410,
        "WIND_ONSHORE":4067,
        "solar":4068,
        "PRICE_DE":4169
    }
    region={
        "DeLU":"DE-LU"
    }
    try:
        print(urljoin(BASE_URL, endpoints["TIMESTAMPS"]))
        # response1=requests.get(U)
    except Exception as e:
        '''
        '''

    try:
        print(urljoin(BASE_URL, endpoints["TIME_SERIES_CHART"]))
    except Exception as e:
        '''
        '''

    return ""

def main():
    responsed_data=callEndPoints()

if __name__=="__main__":
    main()