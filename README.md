# Real-Time Metro Destination Prediction (Demo)

本仓库演示论文中的实时个体目的地预测流程：  
**时空画像匹配（唯一/多候选） → 分类器回退（RF / NB） → 无画像标记（供 HPA 聚合用）。**  
数据为合成样例，目的是帮助复现实时推理逻辑；不包含真实城市数据。

## 文件

- `metro_rt_dest_demo.xlsx` — 示例数据工作簿（6 个 sheet）  
- `predict.py` — 预测脚本（支持 RF / NB 分类器回退）

## 依赖

- Python 3.8+
- pandas, numpy
- scikit-learn

安装（如需要）：
```bash
pip install -U pandas numpy scikit-learn
```

## Excel 数据格式

工作簿：`metro_rt_dest_demo.xlsx`，包含以下 sheet：

### 1) `entries_2018-04-30_xinjiekou`
实时进站事件（示例为**新街口站** 2018-04-30 的进站记录）：
| 列名 | 类型 | 说明 |
|---|---|---|
| event_id | str | 事件 ID |
| event_time | str | ISO 时间戳，例如 `2018-04-30T08:05:00` |
| passenger_id | str | 乘客 ID |
| origin_station_id | int | 进站站点 ID |

### 2) `profile_spatiotemporal`
离线 DBSCAN/规则提取得到的**时空画像**（按乘客/站点/时间桶）：
| 列名 | 类型 | 说明 |
|---|---|---|
| passenger_id | str | 乘客 ID |
| origin_station_id | int | 起点站 ID |
| time_bucket_start_min | int | 时间桶起（分钟） |
| time_bucket_end_min | int | 时间桶止（分钟） |
| dest_station_id | int | 候选目的地站 |
| freq | int | 历史频次 |
| prob | float | 候选概率（可为空，代码会回退用频次归一化） |

> 推理时：  
> - 若唯一匹配 → 直接命中；  
> - 若多候选 → 按 `prob`（或 `freq` 归一化）进行蒙特卡洛抽样。

### 3) `profile_attributes`
离线聚类得到的**属性/偏好画像**（用于分类器回退）：
| 列名 | 类型 | 说明 |
|---|---|---|
| passenger_id | str | 乘客 ID |
| category | str | 乘客类别（如 `shopping_pref`、`commute_flexible`、`no_pref` 等） |
| pref_cluster | int | 偏好聚类 ID（示例整型占位） |
| home_station_id | int | 可选，家/常驻站 |
| origin_station_function | str | 可选，站点功能标签 |

> 若无时空匹配但存在此表画像，则调用分类器（RF/NB）回退预测。

### 4) `stations`
站点主数据（示例）：
| station_id | station_name | line_id | lat | lon |

### 5) `config`
简单配置（示例）：
| key | value |
|---|---|
| time_bucket_size_min | 30 |

### 6) `clf_training`
**分类器训练样本（合成）**：  
用于在程序启动时训练一个小模型，展示“离线训练、在线推理”的流程。
| 列名 | 说明 |
|---|---|
| origin_station_id, hour, category, pref_cluster | 特征 |
| dest_station_id | 标签（目的地站 ID） |

> 真实项目中，这部分应由历史 AFC + 外部数据构建；示例仅用于可运行演示。

## 使用方法

### 方式 A：默认参数直接运行
```bash
python predict.py
```
默认参数：
- `--excel metro_rt_dest_demo.xlsx`
- `--sheet entries_2018-04-30_xinjiekou`
- `--clf rf`（回退分类器使用 RandomForest，可选 `nb` 或 `none`）
- `--out predictions.csv`

### 方式 B：指定参数
```bash
python predict.py --excel metro_rt_dest_demo.xlsx                   --sheet entries_2018-04-30_xinjiekou                   --clf nb                   --out preds_nb.csv
```

## 输出

`predictions.csv`，列包含：
| 列名 | 说明 |
|---|---|
| event_id | 原始事件 ID |
| event_time | 事件时间 |
| passenger_id | 乘客 ID |
| origin_station_id | 进站站点 ID |
| dest_pred | **预测目的地站 ID**（若空则表示回退到 HPA 聚合处理） |
| decision_path | 决策路径：`match_unique`（唯一时空命中）、`match_mc`（多候选抽样）、`clf_fallback`（分类器回退）、`no_st_match_attr_available`（有属性但未启用分类器）、`no_profile`（完全无画像，待 HPA） |

## 决策逻辑（与你论文一致）

1. **时空画像匹配**
   - 唯一候选 → `match_unique`
   - 多候选 → `match_mc`（按 `prob` 或 `freq` 归一化抽样）

2. **分类器回退**
   - 无时空匹配，但 `profile_attributes` 有该乘客画像 → 调用 RF/NB（已在启动时用 `clf_training` 离线训练）

3. **无画像兜底**
   - `no_profile`：在线阶段仅记录入站量，**聚合层**用 HPA（历史概率分配）分配 OD

> 注：本 demo 不包含 HPA 聚合实现；聚合通常在系统的 OD 汇总模块中执行（按 5/15/30 分钟等时间粒度）。

## 选择分类器

- `--clf rf`：随机森林（默认，稳健、推理毫秒级）
- `--clf nb`：朴素贝叶斯（轻量、推理毫秒级）
- `--clf none`：禁用分类器回退（用于仅验证时空画像路径）

## 实时性说明

- **离线**：时空特征抽取、聚类、分类器训练（RF/NB）均在离线完成。  
- **在线**：仅查画像表 + 轻量推理（毫秒级）。  
- 在论文的“时效性”实验中，可统计：单个乘客预测耗时（如 `~ms`）、按 15 分钟粒度聚合 OD 的处理时间（通常 `<0.05 s/OD` 级）。

## 注意事项

- 所有数据为合成示例，仅用于演示调用流程。  
- 真实系统需替换：
  - `profile_spatiotemporal`（由真实 DBSCAN 提取得到）
  - `profile_attributes`（由真实聚类与外部数据构建）
  - `clf_training`（由历史样本构建）  
- HPA 聚合（不活跃/单程票乘客的分配）应在 OD 聚合模块实现。
