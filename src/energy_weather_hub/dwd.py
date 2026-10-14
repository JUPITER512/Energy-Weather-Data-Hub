
import requests
import pandas as pd

def convert_text_csv(filepath):
    with open(filepath,"r",encoding="utf-8") as f:
        print(f)

    # df1=pd.read_csv(filepath)
    # df1.to_csv("station_list.csv")
    # stundenwerte = hourly values
    # TU = air temperature (Temperatur)
    # 00044 = weather station ID
    # akt = current/recent dataset

def main():
    url_txt_dwd = ("https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/air_temperature/recent/TU_Stundenwerte_Beschreibung_Stationen.txt")

    try:
        response = requests.get(url_txt_dwd, timeout=30)
        response.raise_for_status()
        text=response.content.decode("latin-1")
        with open("station_list.txt","w",encoding="utf-8") as file:
            file.write(text)
        print("File downloaded successfully.")

    except requests.RequestException as e:
        print(f"Error downloading the DWD file: {e}")
    except OSError as e:
        print(f"Error writing the file: {e}")
    return "station_list.txt"

if __name__ == "__main__":
#    text_file_path= main()
   convert_text_csv("station_list.txt")
