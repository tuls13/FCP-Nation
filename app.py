from flask import Flask, render_template
import requests
import time
from datetime import datetime, timedelta
from stations import STATION_LIST, CATEGORIES

app = Flask(__name__)
API_URL_7 = "https://api.ffwc.gov.bd/data_load/seven-days-forecast-waterlevel-24-hours/"

# Build STATION_MAP using the correct key "dangerlevel"
STATION_MAP = {
    station['id']: {
        "name": station['name'],
        "danger_level": float(station.get('dangerlevel')) if station.get('dangerlevel') not in (None, "") else None,
        "river": station.get('river')
    }
    for station in STATION_LIST if 'id' in station and 'name' in station
}

CACHE = {}
CACHE_TIMEOUT = 1800  # seconds (30 minutes)

def fetch_forecast(api_url):
    resp = requests.get(api_url)
    resp.raise_for_status()
    return resp.json()

def parse_station_data(date_dict, danger_level, max_date):
    station_data = []
    for date_str, wl_value in date_dict.items():
        try:
            mm, dd, yyyy = map(int, date_str.split("-"))
            iso_date = datetime(yyyy, mm, dd).date()
            if isinstance(wl_value, (int, float)):
                station_data.append({
                    "date": iso_date.isoformat(),
                    "water_level": wl_value
                })
        except Exception:
            continue
    station_data.sort(key=lambda x: x["date"])
    return station_data

def fetch_data():
    now = datetime.now().date()
    max_date = now + timedelta(days=1)
    data_7 = fetch_forecast(API_URL_7)
    all_data = {}

    for id_str, date_dict in data_7.items():
        try:
            station_id = int(id_str)
        except ValueError:
            continue
        station_info = STATION_MAP.get(station_id)
        if not station_info:
            continue
        station_name = station_info["name"]
        danger_level = station_info.get("danger_level")
        river = station_info.get("river")
        station_data = parse_station_data(date_dict, danger_level, max_date)
        all_data[station_name] = {
            "data": station_data,
            "danger_level": danger_level,
            "river": river
        }
    return all_data

def fetch_data_cached():
    now = time.time()
    if "data" in CACHE and now - CACHE.get("time", 0) < CACHE_TIMEOUT:
        return CACHE["data"]
    data = fetch_data()
    CACHE["data"] = data
    CACHE["time"] = now
    return data

@app.route("/", methods=["GET"])
def index():
    current_date = datetime.now().date()
    all_data = fetch_data_cached()

    # Build a mapping from station name to category
    station_to_category = {
        station: category
        for category, stations in CATEGORIES.items()
        for station in stations
    }

    # Only include stations above danger level in the next 2 days
    filtered_station_data = {}
    for name, info in all_data.items():
        above = False
        for entry in info["data"]:
            entry_date = datetime.fromisoformat(entry["date"]).date()
            if current_date <= entry_date <= current_date + timedelta(days=2):
                if info["danger_level"] is not None and entry["water_level"] > info["danger_level"]:
                    above = True
                    break
        if above:
            info["category"] = station_to_category.get(name, "")
            filtered_station_data[name] = info

    return render_template(
        "index.html",
        categories=CATEGORIES,
        current_date=current_date.strftime("%B %d, %Y"),
        station_data=filtered_station_data
    )

@app.route("/category/<category_name>")
def category_page(category_name):
    all_data = fetch_data_cached()
    stations = CATEGORIES.get(category_name, [])
    station_data = {}
    for station in stations:
        info = all_data.get(station, {
            "data": [],
            "danger_level": None,
            "river": None
        })
        if info["data"]:
            info["category"] = category_name
            station_data[station] = info
    return render_template("category.html", category=category_name, station_data=station_data)
