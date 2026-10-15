import pandas as pd
import requests
from urllib.parse import urljoin
import json
import time

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
ENDPOINTS={
    "TIMESTAMPS":"chart_data/{filter}/{region}/index_hour.json",
    "TIME_SERIES_CHART":"chart_data/{filter}/{region}/{filterCopy}_{regionCopy}_hour_{timestamp}.json",
    "TIME_SERIES_TABLE":"table-data/{filter}/{region}/{filterCopy}_{regionCopy}_quarterhour_{timestamp}.json",
}
FILTERS = {
    "LOAD_DE": 410,
    "WIND_ONSHORE": 4067,
    "SOLAR": 4068,
    "PRICE_DE": 4169,
}

REGIONS = {
    "LOAD_DE": "DE",
    "WIND_ONSHORE": "DE",
    "SOLAR": "DE",
    "PRICE_DE": "DE-LU",
}



def fetch_weeks(filter_id,region,n_weeks=5):
    ts_response=requests.get(urljoin(BASE_URL, ENDPOINTS["TIMESTAMPS"].format(filter=filter_id,region=region)),timeout=30)
    ts_response.raise_for_status()
    needed_ts = ts_response.json()["timestamps"][-n_weeks:]

    rows=[]
    for ts in needed_ts:
        data_chunk=requests.get(
            urljoin(BASE_URL,ENDPOINTS["TIME_SERIES_CHART"]
                    .format(
                        filter=filter_id,filterCopy=filter_id,region=region,regionCopy=region,timestamp=ts
                    )
                    ),
            timeout=30
        )
        data_chunk.raise_for_status()
        rows.extend(data_chunk.json()["series"])
    return rows


def to_dataframe(rows, series_name):
    df = pd.DataFrame(rows, columns=["ts_ms", "value"])
    df["ts_utc"] = pd.to_datetime(df["ts_ms"], unit="ms", utc=True)
    df["ts_berlin"] = df["ts_utc"].dt.tz_convert("Europe/Berlin")
    df["series"] = series_name
    return df[["series", "ts_utc", "ts_berlin", "value"]]

def fetch_all_series(n_weeks):
    frames=[]
    for name, filter_id in FILTERS.items():
        region = REGIONS[name]
        rows = fetch_weeks(filter_id, region, n_weeks=n_weeks)
        frames.append(to_dataframe(rows, name))
        print(f"{name}: {len(rows)} rows ({region})")
    return pd.concat(frames, ignore_index=True)

    
def main():
    smard=fetch_all_series(n_weeks=5)
    print(smard.head())
    print(smard.dtypes)
    print(f"Total rows: {len(smard)}")
    smard.to_csv("smard_data.csv", index=False)
    

if __name__=="__main__":
    main()