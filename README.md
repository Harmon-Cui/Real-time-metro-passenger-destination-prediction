[![DOI](https://zenodo.org/badge/1069326174.svg)](https://doi.org/10.5281/zenodo.17263980)
# Real-Time Metro Destination Prediction (Demo)

This repository provides a demonstration of the **real-time individual-level destination prediction workflow**:  
**Spatiotemporal profile matching (unique/multiple candidates) → Classifier fallback (RF / NB) → Unprofiled marking (for HPA aggregation).**  
The dataset is fully synthetic, designed to illustrate the inference logic without disclosing real metro AFC data.

## Files

- `metro_rt_dest_demo.xlsx` — Demo dataset workbook (6 sheets)  
- `predict.py` — Prediction script (with RF / NB fallback)  
- `README.md` — Documentation

## Dependencies

- Python 3.8+  
- pandas, numpy  
- scikit-learn  

Install dependencies:
```bash
pip install -U pandas numpy scikit-learn
```

## Excel Data Format

The workbook `metro_rt_dest_demo.xlsx` contains the following sheets:

### 1) `entries_2018-04-30_xinjiekou`
Synthetic real-time entry events (example: **Xinjiekou station**, April 30, 2018):
| Column | Type | Description |
|---|---|---|
| event_id | str | Event ID |
| event_time | str | ISO timestamp, e.g., `2018-04-30T08:05:00` |
| passenger_id | str | Passenger ID |
| origin_station_id | int | Entry station ID |

### 2) `profile_spatiotemporal`
Offline DBSCAN/rule-based spatiotemporal profiles (per passenger/station/time bucket):
| Column | Type | Description |
|---|---|---|
| passenger_id | str | Passenger ID |
| origin_station_id | int | Entry station |
| time_bucket_start_min | int | Start of time bucket (minutes) |
| time_bucket_end_min | int | End of time bucket (minutes) |
| dest_station_id | int | Candidate destination |
| freq | int | Historical frequency |
| prob | float | Candidate probability (optional; if empty, fallback to normalized freq) |

> - Unique candidate → `match_unique`  
> - Multiple candidates → `match_mc` (Monte Carlo sampling based on prob/freq)

### 3) `profile_attributes`
Offline clustering results with passenger attributes/preferences (for classifier fallback):
| Column | Type | Description |
|---|---|---|
| passenger_id | str | Passenger ID |
| category | str | Passenger category (`shopping_pref`, `commute_flexible`, `no_pref`, etc.) |
| pref_cluster | int | Preference cluster ID |
| home_station_id | int | Optional: home station |
| origin_station_function | str | Optional: station functional tag |

> If no spatiotemporal match but profile exists here → classifier fallback (RF/NB).

### 4) `stations`
Station master data (example):
| Column | Description |
|---|---|
| station_id | Station ID |
| station_name | Name |
| line_id | Metro line |
| lat | Latitude |
| lon | Longitude |

### 5) `config`
Configuration parameters:
| key | value |
|---|---|
| time_bucket_size_min | 30 |

### 6) `clf_training`
Synthetic training samples for classifiers (used to train RF/NB at startup):
| Feature columns | Target |
|---|---|
| origin_station_id, hour, category, pref_cluster | Features |
| dest_station_id | Label (destination station) |

---

## Usage

### Option A: Run with default settings
```bash
python predict.py
```
Defaults:
- `--excel metro_rt_dest_demo.xlsx`
- `--sheet entries_2018-04-30_xinjiekou`
- `--clf rf` (Random Forest fallback; options: `nb`, `none`)
- `--out predictions.csv`

### Option B: Specify parameters
```bash
python predict.py --excel metro_rt_dest_demo.xlsx                   --sheet entries_2018-04-30_xinjiekou                   --clf nb                   --out preds_nb.csv
```

---

## Output

`predictions.csv` contains:
| Column | Description |
|---|---|
| event_id | Event ID |
| event_time | Timestamp |
| passenger_id | Passenger ID |
| origin_station_id | Entry station |
| dest_pred | Predicted destination station (empty if routed to HPA) |
| decision_path | Decision path: `match_unique`, `match_mc`, `clf_fallback`, `no_st_match_attr_available`, `no_profile` |

---

## Decision Logic

1. **Spatiotemporal profile match**  
   - Unique → `match_unique`  
   - Multiple → `match_mc` (Monte Carlo sampling)  

2. **Classifier fallback**  
   - If no spatiotemporal match but profile exists → apply RF/NB (trained on `clf_training`)  

3. **Unprofiled passengers**  
   - `no_profile`: these are counted for entry volumes; in the real system, OD flows are allocated via Historical Proportion Allocation (HPA) during aggregation.  

---

## Classifier Options
- `--clf rf`: Random Forest (default)  
- `--clf nb`: Naïve Bayes (lightweight)  
- `--clf none`: disable fallback classifiers (profiling only)  

---

## Runtime Feasibility

- **Offline**: Feature extraction, clustering, and classifier training (RF/NB).  
- **Online**: Only table lookups + lightweight predictions (milliseconds).  
- In experiments, per-passenger prediction took ~ms, and OD aggregation at 15-min granularity required `<0.05s` per OD pair.  

---

## Notes

- All data are **synthetic examples** for demonstration only.  
- Replace with real AFC-derived profiles and attributes for actual deployment.  
- HPA aggregation is not implemented in this demo (to be handled in OD aggregation module).  
