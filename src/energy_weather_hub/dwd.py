import requests
import pandas as pd
import re
import zipfile
from urllib.parse import urljoin
import io

GERMAN_STATES = sorted([
    "Baden-Württemberg", "Bayern", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen",
    "Mecklenburg-Vorpommern", "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz",
    "Saarland", "Sachsen", "Sachsen-Anhalt", "Schleswig-Holstein", "Thüringen",
], key=len, reverse=True)

Base_URL = ("https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/recent/")
Station_List_Url=urljoin(Base_URL,"TU_Stundenwerte_Beschreibung_Stationen.txt")

def download_zips(station_id,zipfiles):
    stationid=int(station_id)

    station_code=f"{stationid:05d}"
    matches = [
        (filename,url) 
        for filename,url in zipfiles.items()
        if re.search(
            rf"TU_{station_code}_",
            filename,
            re.IGNORECASE
        )
    ]
    if not matches:
        print(f"No recent ZIP found for station {station_code}")
        return None
    filename,url=matches[0]

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip:
        produkt_files=[
            name for name in zip.namelist()
            if name.rsplit("/",1)[-1].startswith("produkt_") and name.lower().endswith(".txt")
        ]

        if not produkt_files:
            print(f"No produkt_ file in {filename}")
            return None

        with zip.open(produkt_files[0]) as f:
            df=pd.read_csv(
                f,
                sep=";",
                encoding='latin-1',
                dtype={"STATIONS_ID":"string"},
                # na_values=[]
                na_values=["-999", "-999.0", "-9999"],
                keep_default_na=True,
                skipinitialspace=True
            )
    df.columns = df.columns.str.strip()

    for col in df.select_dtypes(include="object").columns:
        df[col]=df[col].str.strip()

    df["MESS_DATUM"]=pd.to_datetime(
        df["MESS_DATUM"].astype(str).str.strip(),
        format="%Y%m%d%H",
        utc=True,
        errors="coerce"
    )

    for col in df.columns:
        if col not in ("STATIONS_ID","MESS_DATUM","eor"):
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["MESS_DATUM"])
    df["STATIONS_ID"] = station_id
    print(f"Downloaded {station_code}: {len(df)} rows")
    return df























def find_station_zip():
    "trying to find the station zips "
    response=requests.get(Base_URL,timeout=30)
    response.raise_for_status()
    filenames=re.findall(r'href=["\']([^"\']+\.zip)["\']',response.text,flags=re.IGNORECASE)

    return{name:urljoin(Base_URL,name) for name in filenames}

def download_station_list():
    try:
        response = requests.get(Station_List_Url, timeout=30)
        response.raise_for_status()
        text=response.content.decode("latin-1")

    except requests.RequestException as e:
        print(f"Error downloading the DWD file: {e}")
    except OSError as e:
        print(f"Error writing the file: {e}")


    stations=[]
    for line in text.splitlines()[2:]:
        # print(line)
        if not line.strip():
            continue
        station_id, von, bis, height, lat, lon, rest =line.split(maxsplit=6)
        rest=rest.rstrip()
        last_word_start=rest.rfind(" ")
        rest=rest[:last_word_start].rstrip() if last_word_start!=-1 else rest
        state= next(
            (s for s in GERMAN_STATES if rest.lower().endswith(s.lower())),
            None
        )
        name = rest[:-len(state)].strip() if state else rest.strip()
        stations.append({
            "STATIONS_ID": int(station_id),
            "FROM_DATE": von,
            "TO_DATE": bis,
            "HEIGHT": float(height),
            "LATITUDE": float(lat),
            "LONGITUDE": float(lon),
            "STATION_NAME": name,
            "STATE": state,
        })
    return pd.DataFrame(stations)
def main():
    station_list_dataframe=download_station_list()
    print(f"Parsed {len(station_list_dataframe)} stations")
    zip_files = find_station_zip()
    print(f"Found {len(zip_files)} ZIP files")


    available_ids=set()
    for filename in zip_files:
        match=re.search(r"TU_(\d{5})_",filename,re.IGNORECASE)
        if match:
            available_ids.add(int(match.group(1)))


    candidates=station_list_dataframe[station_list_dataframe['STATIONS_ID'].isin(available_ids)].copy()
    selected=candidates.head(15)
    if selected.empty:
        raise RuntimeError("No matching station ZIPs found. Check the current DWD directory listing and filenames.")

    frames=[]
    for id in selected['STATIONS_ID']:
        try:
            df=download_zips(id,zip_files)
            if df is not None and not df.empty:
                frames.append(df)
        except (requests.RequestException,zipfile.BadZipFile,pd.errors.ParserError,KeyError,ValueError) as e:
            print(f"Station Id {id} failed {e}")
    if not frames:
        raise RuntimeError("No station data could be downloaded.")
    
    hourly = pd.concat(frames,ignore_index=True)
    hourly = hourly.sort_values(["STATIONS_ID", "MESS_DATUM"]).reset_index(drop=True)
    station_list_dataframe.to_csv("stations.csv",index=False)
    hourly.to_csv("hourly_temperature.csv",index=False)
    print(hourly.head())
    print(hourly.dtypes)
    print(f"Total observations: {len(hourly)}")
if __name__ == "__main__":
    main()

