# Hierarchical Passenger Clustering and Segmentation

This document describes the **offline hierarchical passenger clustering workflow**
corresponding to Section 2.2 of the paper.
It is provided to clarify the analytical stages and inputs used to derive passenger
categories, thereby supporting transparency and reproducibility of the proposed framework.

This file is **workflow-level documentation** and does not constitute an executable
implementation of the clustering algorithms described in the manuscript.

---

## 1. Workflow Overview

The hierarchical clustering procedure integrates:

- **Pre-classification** (card type and activity screening),
- **Second-order clustering** (segmentation of active passengers),
- **Fine-grained clustering** (for passengers remaining difficult to categorize).

All clustering and segmentation steps are conducted as **offline analytical procedures**
and produce passenger group labels for downstream destination prediction and OD aggregation.

---

## 2. Pre-classification: Card Type and Activity Screening

Passengers are first divided by ticket type into:

- **Card-holding passengers** (with identifiable passenger IDs),
- **Non-card-holding passengers** (without persistent passenger IDs).

For card-holding passengers, historical travel frequency is compared against the global
threshold `MinPts` (defined in Section 2.1.1 of the paper):

- Passengers with travel frequency below `MinPts` are defined as **inactive passengers**,
  for whom meaningful spatiotemporal features cannot be reliably extracted.
- The remaining card-holding passengers are treated as **active passengers** and enter
  the hierarchical clustering process.

---

## 3. Second-Order Clustering of Active Passengers (Implemented in SPSS)

### 3.1 Inputs

Second-order clustering is performed using both:

- **Spatiotemporal travel feature indicators** extracted from AFC data, including:
  - Travel randomness index ($NR_u$),
  - Travel periodicity and regularity indicators,
  - Travel intensity and stability indicators;
- **Preference-related indicators**, such as station functional type attributes.

All numerical features are normalized prior to clustering.

### 3.2 Procedure and Outputs

The second-order clustering stage is implemented using **SPSS** as an offline statistical
analysis tool.

Based on the resulting clusters and the randomness indicator ($NR_u$):

- The cluster with the lowest $NR_u$ is identified as **deterministic passengers**
  (commuting population), characterized by highly regular spatiotemporal patterns.
- The remaining clusters are categorized as **non-commuting passengers**, including both
  partially regular travelers and passengers with sparse or irregular travel behaviors.

Cluster quality is assessed using silhouette-based measures provided by SPSS to ensure
reasonable separation and robustness.

This definition aligns with the conventional commuting versus non-commuting dichotomy
in the literature while ensuring that the subsequent modeling framework focuses on the
more heterogeneous and challenging non-commuting group.

---

## 4. Fine-Grained Clustering Guided by Fuzzy C-Means (FCM) Principles

For passengers whose behavioral patterns remain difficult to categorize after the
second-order clustering stage, a fine-grained clustering step is conducted.

In the manuscript, **Fuzzy C-Means (FCM)** is introduced to describe the methodological
principle of allowing partially overlapping behavioral characteristics across groups.
Compared with hard clustering methods (e.g., K-means), this principle is suitable for
urban rail transit passenger data, where many individuals—especially non-commuting
passengers—exhibit overlapping and irregular travel patterns.

At the implementation level, this step is conducted as an **offline statistical grouping
and post-analysis procedure**, guided by fuzzy clustering principles rather than by a
standalone algorithmic realization of FCM.

The number of clusters is determined through cluster validity analysis (e.g., the
Davies–Bouldin Index, DBI), supporting a data-driven and robust partition.

---

## 5. Outputs, Aggregation, and Interpretation

The hierarchical clustering workflow yields **discrete passenger categories**, which are
summarized through class-wise statistical aggregation, including:

- Passenger counts and proportions,
- Aggregated trip volumes,
- Mean behavioral indicators within each category.

Final passenger groups are interpreted and labeled according to dominant behavioral and
consumption characteristics (e.g., shopping-preference, entertainment-preference,
dining-preference, and no-significant-preference passengers). These labels are obtained
through post-analysis interpretation rather than direct algorithmic outputs and are used
as inputs for downstream prediction modules.

---

## 6. Notes on Reproducibility

- **Second-order clustering** is implemented using **SPSS** as an offline statistical tool.
- Fine-grained clustering follows **fuzzy clustering principles** without relying on a
  standalone FCM implementation provided in this repository.
- This documentation clarifies the offline analytical workflow and does not imply the
  availability of executable clustering code.
- The resulting passenger categories correspond to those reported in the manuscript
  tables and figures.

For details on feature extraction and downstream modeling, please refer to the
accompanying code modules and the main paper.
