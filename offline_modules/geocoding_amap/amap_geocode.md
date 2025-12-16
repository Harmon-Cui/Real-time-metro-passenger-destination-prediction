# Station Geocoding Using Amap Open Platform

This module retrieves geographic coordinates (longitude and latitude)
for metro stations using the Amap (Gaode) Open Platform. The resulting
station-level geolocation data are used as spatial references for
subsequent analyses, including POI aggregation, geo-economic feature
mapping, and OD spatial representation.

---

## Data Source

Station geocoding is performed via the Amap Open Platform
(https://lbs.amap.com), which provides authoritative geocoding services
for addresses and place names in China.

---

## Input and Output

**Input**:
- Metro station names (text format, one station per row)

**Output**:
- Station-level geographic coordinates:
  - Longitude
  - Latitude

The output is stored in a tabular format (e.g., CSV or Excel) for
subsequent spatial processing.

---

## Processing Logic

For each station name, the module sends a geocoding request to the Amap
API and parses the returned longitude–latitude coordinates. The resulting
coordinates are then associated with the corresponding station identifiers.

---

## Usage in the Proposed Framework

The extracted station coordinates serve as fundamental spatial attributes
in the proposed framework. Specifically, they are used to:

- Match AFC records with spatial locations
- Define station service areas
- Aggregate POI and geo-economic indicators around stations
- Support spatial distance calculations in OD-related analyses

---

## Reproducibility Notes

The geocoding process relies on the Amap Open Platform and requires a valid
API key. Due to platform usage policies, the API key and raw query results
are not publicly released. Nevertheless, the data source and processing
logic are explicitly documented, allowing other researchers to reproduce
the geocoding procedure using their own Amap API credentials.

