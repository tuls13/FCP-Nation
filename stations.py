# stations.py

import requests
import re

def normalize_name(name):
    """Normalize station names for consistent lookup."""
    return re.sub(r'[^a-z0-9]', '', name.lower())

def fetch_stations():
    """Fetch the latest station list from FFWC API."""
    url = "https://api.ffwc.gov.bd/data_load/stations/?format=json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Fetch stations at module load (consider caching if used often)
STATION_LIST = fetch_stations()

# Build a lookup for normalized station names to actual names in STATION_LIST
STATION_NAME_LOOKUP = {
    normalize_name(station['name']): station['name']
    for station in STATION_LIST
}

def get_station_name_by_id(station_id):
    """Get station name by ID from the fetched station list."""
    for station in STATION_LIST:
        if station["id"] == station_id:
            return station["name"]
    return f"Unknown ID {station_id}"

# Define categories (regions)
CATEGORIES = {
    "Sylhet Region": [
        "Bhairabbazar", "Habiganj", "Manu-RB", "Moulvibazar", "Sherpur-Sylhet", "Mymensingh", "Sylhet",
        "Amalshid", "Sheola", "Jamalpur", "Jariajanjail", "Kanaighat", "Sunamganj", "Bahadurabad",
        "Durgapur", "Sarighat", "Nakuagaon", "Lourergorh", "Kalmakanda", "Dewanganj", "Netrokona",
        "Khaliajuri", "Jaflong", "Derai", "Zakiganj", "Markuli"
    ],
    "Rajshahi Region": [
        "Rajshahi", "Serajganj", "Atrai", "C-Nawabganj", "Mohadevpur", "Bogra", "Chakrahimpur",
        "Naogaon", "Rohanpur", "Gaibandha", "Chilmari", "Fulchari", "Nilphamari", "Kaunia",
        "Kurigram", "Panchagarh", "Thakurgaon", "Dinajpur"
    ],
    "Dhaka Region": [
        "Madaripur", "Sureshswar", "Bhagyakul", "Faridpur", "Hariharpara", "Narayanganj", "Dhaka",
        "Demra", "Goalondo", "Mirpur", "Taraghat", "Aricha", "Jagir", "Tongi", "Nayarhat"
    ],
    "Khulna Region": [
        "Mongla", "Shakra", "Khulna", "Kalaroa", "Jhikargacha", "Kamarkhali", "Chuadanga",
        "Hatboalia", "Gorai-RB", "Hardinge-RB", "Bagerhat", "Morelganj", "Satkhira", "Kaliganj",
        "Assasuni", "Shyamnagar", "Debhata", "Tala", "Dumuria", "Paikgachha", "Koyra", "Dacope"
    ],
    "Barishal Region": [
        "Daulatkhan", "Bhola", "Manpura", "Barisal", "Patuakhali", "Kalapara", "Barguna",
        "Jhalokathi", "Rajapur", "Kuakata", "Mathbaria", "Amtali"
    ],
    "Chattogram Region": [
        "Chiringa", "Lama", "Dohazari", "Bandarban", "Panchpukuria", "Narayanhat", "Ramgarh",
        "Chandpur", "Parshuram", "Comilla", "Jibanpur", "Hatia", "Chittagong"
    ]
}

# Filter CATEGORIES to only include stations present in STATION_LIST
for cat, stations in CATEGORIES.items():
    filtered = [
        STATION_NAME_LOOKUP[normalize_name(s)]
        for s in stations if normalize_name(s) in STATION_NAME_LOOKUP
    ]
    CATEGORIES[cat] = filtered

if __name__ == "__main__":
    print("Sylhet Region stations:", CATEGORIES["Sylhet Region"])
