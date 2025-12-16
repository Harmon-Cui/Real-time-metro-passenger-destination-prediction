# Normalization of POI and Geo-Economic Features

This document describes the normalization and aggregation procedures
applied to external data sources, including POI information and
geo-economic indicators, to construct station-level features that are
consistent with the proposed modeling framework.

---

## Data Sources

Two types of external data are considered:

1. **POI data**  
   - Obtained from the Amap (Gaode) Open Platform  
   - Includes fine-grained building- or facility-level POI records with
     category labels and geographic coordinates

2. **Geo-economic data**  
   - Includes housing rental prices, housing sale prices, and
     consumption-related indicators  
   - Collected using third-party data collection tools from relevant
     online platforms

Due to platform usage policies and data confidentiality constraints,
the raw external datasets are not publicly released.

---

## Spatial Aggregation

To align external data with the station-based modeling framework, all
POI and geo-economic records are aggregated at the station level.

- A predefined service area is defined for each station
- POI and geo-economic records located within the service area are
  associated with the corresponding station
- Spatial matching is performed based on geographic proximity

---

## POI Feature Normalization

Fine-grained POI categories are merged into a set of land-use types,
including:

- Residential
- Green/open space
- Commercial
- Public management and service
- Transportation facilities

For each station, POI-based features are constructed using aggregated
statistics, such as counts or proportions of different land-use types.

---

## Geo-Economic Feature Normalization

Geo-economic indicators are normalized to ensure comparability across
stations:

- Housing rental and sale prices are aggregated using summary statistics
  (e.g., mean or median values) within each station’s service area
- When necessary, logarithmic transformation or standardization is
  applied to reduce scale differences

The resulting indicators reflect the relative socio-economic context
and commercial vitality around each station.

---

## Output Features

After normalization, each station is associated with a vector of
external features, including land-use composition and geo-economic
attributes. These station-level features are then integrated with AFC-
derived behavioral features for downstream passenger profiling and
destination prediction.

---

## Reproducibility Notes

Normalization refers to the station-level aggregation and feature
scaling procedures described above, rather than raw data crawling.
By explicitly documenting the data sources and normalization logic,
this module enables methodological reproducibility without requiring
the release of proprietary external datasets.

