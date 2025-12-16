# Hierarchical Passenger Clustering and Segmentation

This document describes the **offline hierarchical passenger clustering workflow**
corresponding to Section 2.2 of the paper.
The purpose of this documentation is to clarify the analytical logic and processing stages
used to derive passenger categories, thereby supporting transparency and reproducibility
of the proposed framework.

This module provides **methodological and workflow-level documentation only** and does
not represent an executable clustering algorithm.

---

## 1. Overview

The hierarchical clustering framework integrates **pre-classification, coarse clustering,
and fine-grained segmentation** to progressively refine individual passenger groups.
The overall objective is to distinguish deterministic (commuting) passengers from
non-commuting passengers and further characterize heterogeneous preference-driven
travel behaviors.

All clustering and segmentation steps are conducted as **offline analytical procedures**
and provide behavioral labels for downstream real-time destination prediction models.

---

## 2. Pre-classification of Passengers

Passengers are first divided according to ticket type into:

- **Card-holding passengers**, with identifiable passenger IDs;
- **Non-card-holding passengers**, without persistent IDs.

Among card-holding passengers, historical travel frequency is evaluated using the global
threshold `MinPts` (defined in Section 2.1.1 of the paper):

- Passengers with travel frequency below `MinPts` are labeled as **inactive passengers**,
  for whom meaningful spatiotemporal features cannot be reliably extracted.
- The remaining passengers are considered **active passengers** and are used in the
  hierarchical clustering process.

---

## 3. Second-Order Clustering of Active Passengers (SPSS-based)

### 3.1 Input Features

Second-order clustering is performed using a combination of:

- Spatiotemporal travel features derived from AFC data, including:
  - Travel randomness index ($NR_u$)
  - Travel periodicity
  - Travel intensity and stability indicators
- Preference-related contextual attributes, such as station functional types

All numerical features are normalized prior to analysis.

---

### 3.2 Coarse Classification

The second-order clustering of active passengers is implemented using **SPSS**
as an offline statistical analysis tool.

Active passengers are grouped based on their spatiotemporal regularity:

- Passengers with low values of $NR_u$ and highly regular patterns are classified as
  **deterministic passengers**, corresponding to commuting travelers.
- All remaining active passengers are categorized as **non-commuting passengers**,
  including both partially regular and highly irregular travelers.

Cluster quality is evaluated using silhouette-based measures provided by SPSS to ensure
reasonable separation and robustness of the resulting groups.

This definition is consistent with the conventional commuting versus non-commuting
dichotomy in the literature, while explicitly focusing subsequent modeling on the
more heterogeneous non-commuting group.

---

## 4. Fine-Grained Segmentation Based on Fuzzy Clustering Principles

For non-commuting passengers whose behavioral patterns remain difficult to characterize
after second-order clustering, a **fine-grained segmentation step** is applied.

In this study, **Fuzzy C-Means (FCM)** is introduced at the **methodological level**
to describe the clustering principle of allowing overlapping behavioral characteristics.
Compared with hard clustering methods (e.g., K-means), this principle is suitable for
urban rail transit passengers whose travel patterns often exhibit partial regularity
and uncertainty.

At the implementation level, this step is conducted as an **offline statistical grouping
and post-analysis procedure**, guided by fuzzy clustering principles rather than by an
explicit algorithmic realization of FCM.

Cluster numbers are determined through cluster validity analysis (e.g., Davies–Bouldin
Index, DBI), ensuring a data-driven and robust partition.

---

## 5. Output and Interpretation

The hierarchical clustering process yields **discrete passenger categories**, which are
summarized using class-wise statistical aggregation, including:

- Passenger counts and proportions;
- Aggregated trip volumes;
- Mean behavioral indicators within each category.

Final passenger groups are **interpreted and labeled** according to dominant behavioral
and consumption characteristics, such as shopping-preference, entertainment-preference,
dining-preference, and no-significant-preference passengers.

These labels are derived through **post-analysis interpretation** rather than direct
algorithmic outputs and are used as inputs for personalized destination prediction
and system-level OD aggregation.

---

## 6. Notes on Reproducibility

- Second-order clustering is implemented using **SPSS** as an offline statistical tool.
- Fine-grained segmentation follows **fuzzy clustering principles** without relying on
  a standalone FCM algorithmic implementation.
- This documentation is intended to explain the analytical workflow and does not imply
  the availability of executable clustering code.
- The resulting passenger categories correspond to those reported in the manuscript
  tables and figures.

For further details on feature extraction and downstream modeling, please refer to
the accompanying code modules and the main paper.
