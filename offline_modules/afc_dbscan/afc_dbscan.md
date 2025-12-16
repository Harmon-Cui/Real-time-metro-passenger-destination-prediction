# AFC-Based Spatiotemporal Feature Extraction Using DBSCAN

This module extracts individual-level spatiotemporal travel features from
Automatic Fare Collection (AFC) transaction records using a DBSCAN-based
density clustering approach. The extracted features are used to characterize
passengers' habitual travel patterns and serve as inputs for downstream
destination prediction and passenger profiling tasks.

---

## Input Data Structure (AFC Transactions)

The DBSCAN-based feature extraction operates on AFC transaction records stored
in a relational database (MySQL in the case study). Each record corresponds to
a completed metro trip.

The required logical fields are summarized below:

| Field name | Description |
|-----------|-------------|
| `TICKET_ID` | Anonymized passenger identifier |
| `OOOO` | Entry timestamp (station entry time) |
| `DDDD` | Exit timestamp (station exit time) |
| `IN_STATION_NAME` | Origin station name |
| `TXN_STATION_NAME` | Destination station name |
| `OD_dui` | Origin–destination (OD) pair, formatted as `O-D` |

Only the above fields are required by this module. Additional operational
fields in the AFC database (e.g., ticket type, transaction flags) are not used
in the clustering process.

---

## Feature Construction

For each passenger (`TICKET_ID`), a trip chain is reconstructed by grouping
AFC records in chronological order. Each trip is encoded into a two-dimensional
feature space consisting of:

1. **Time feature**:  
   Entry time is converted into minutes since midnight.

2. **OD feature**:  
   Each OD pair is mapped to a numeric code to ensure compatibility with
   distance-based clustering.

Thus, each AFC trip is represented as a point in the spatiotemporal feature
space `(time, OD)`.

---

## DBSCAN Clustering

Density-based clustering is applied independently to each passenger's trip
chain using the DBSCAN algorithm.

- Clustering space: `(entry time, OD code)`
- Distance metric: Euclidean distance
- Parameters:
  - `eps`: predefined density radius (minutes-based)
  - `min_samples`: minimum number of trips required to form a valid cluster

Trips that do not belong to any dense region are treated as noise.

---

## Output Spatiotemporal Profiles

For each identified cluster, the following spatiotemporal travel features are
derived:

- Passenger ID
- Cluster ID
- Time window of the cluster (start time – end time)
- Origin station
- Destination station
- Number of trips in the cluster
- Noise ratio (proportion of noise trips)

These cluster-level features constitute the passenger's spatiotemporal travel
profile and are stored for subsequent modeling tasks.

---

## Reproducibility Notes

Due to data confidentiality constraints, the original AFC transaction records
cannot be publicly released. This module operates directly on relational AFC
tables and is therefore database-driven.

Instead of providing a synthetic AFC dataset, we explicitly document the input
data structure and processing logic. This enables other researchers to reproduce
the proposed spatiotemporal feature extraction procedure using their own AFC
datasets with compatible schemas.

