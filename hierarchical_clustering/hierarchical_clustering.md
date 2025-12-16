# Hierarchical Passenger Clustering and Segmentation

This document describes the **offline hierarchical passenger clustering and segmentation workflow** used in this study.  
The purpose of this documentation is to clarify the analytical logic and data processing steps underlying passenger categorization, thereby supporting the interpretability and reproducibility of the proposed framework.  
This module provides **methodological documentation only** and does not represent a standalone algorithmic implementation.

---

## 1. Purpose

Passenger travel behavior in urban rail transit systems exhibits substantial heterogeneity, particularly among non-commuting and irregular users.  
To capture this heterogeneity in a structured and interpretable manner, a **multi-stage (hierarchical) clustering strategy** was adopted to segment active passengers into behaviorally meaningful groups.

The objectives of this clustering process are to:

- Distinguish **deterministic (commuting) passengers** from non-commuting passengers;
- Further characterize **flexible and irregular travel patterns**;
- Identify **preference-oriented passenger groups** to support downstream personalized destination prediction.

All clustering procedures are conducted as **offline statistical analyses** and serve as inputs to the subsequent prediction framework.

---

## 2. Input Features

The hierarchical clustering process is based on a set of **numerical behavioral indicators** derived from AFC data, together with selected contextual attributes.  
All numerical features are normalized prior to analysis.

### 2.1 Spatiotemporal Travel Features

The following indicators are used to characterize passenger travel regularity and intensity:

- Average OD trip count  
- Travel randomness index ($NR_u$)  
- Variance of travel randomness  
- Travel periodicity  
- Distance fluctuation coefficient  
- Number of distinct spatiotemporal travel patterns

These features jointly describe the stability, frequency, and temporal structure of individual travel behavior.

### 2.2 Contextual and Preference-Related Features

For preference-oriented segmentation, additional indicators are incorporated, including:

- Station functional type attributes  
- Aggregated economic attributes associated with passenger activity areas  
  (e.g., living expenditure and consumption expenditure)

These attributes are used to support preference interpretation rather than strict rule-based classification.

---

## 3. Clustering Logic

### 3.1 First-Stage Clustering: Identification of Deterministic Passengers

In the first stage, a statistical clustering analysis is applied to all **active passengers** using the spatiotemporal travel features listed above.

Passengers with **low travel randomness ($NR_u$)** and strong periodic patterns are identified as **deterministic (commuting) passengers**, while the remaining passengers are categorized as non-commuting users.  
Cluster quality is evaluated using silhouette-based measures to ensure reasonable separation.

---

### 3.2 Second-Stage Clustering: Subclassification of Flexible Passengers

Passengers exhibiting partial regularity (i.e., flexible travel behavior) are further clustered using an extended feature set that includes station-type indicators.

This step distinguishes:

- Commute-dominated flexible passengers  
- Non-commuting flexible passengers

The objective is to refine behavioral distinctions while maintaining interpretability for downstream modeling.

---

### 3.3 Preference-Oriented Segmentation (Fuzzy Clustering Principle)

For passengers who remain difficult to characterize after the second stage—particularly those exhibiting high randomness and overlapping behavioral traits—a **fuzzy clustering–based statistical segmentation principle** is adopted.

In this study, the term *fuzzy clustering* is used to describe the **conceptual principle** of capturing overlapping preferences and gradual behavioral differences, rather than to indicate an explicit algorithmic realization of fuzzy C-means (FCM).

This step is implemented as an **offline statistical grouping and post-analysis procedure**, focusing on the relative proximity of passengers across multiple behavioral and economic dimensions.

---

## 4. Output and Interpretation

The output of the hierarchical clustering process consists of **discrete passenger categories**, which are subsequently summarized using class-wise statistical aggregation.

Key characteristics include:

- Passenger counts and proportions per category  
- Aggregated trip volumes  
- Mean behavioral indicators within each group

The final passenger categories are **interpreted and labeled** based on dominant behavioral and consumption patterns, such as:

- Shopping-preference travel passengers  
- Entertainment-preference travel passengers  
- Dining-preference travel passengers  
- Passengers with no significant preference

These labels are assigned through **post-analysis interpretation** rather than direct algorithmic outputs and are used as inputs for personalized destination prediction models.

---

## 5. Implementation Notes

- All clustering analyses are conducted **offline** using standard statistical analysis tools.  
- This documentation is intended to clarify the analytical workflow and does not imply the availability of a standalone clustering algorithm.  
- The resulting passenger categories correspond to those reported in the manuscript tables and figures.

For details on downstream modeling and prediction, please refer to the main paper and the accompanying code modules.

