# agent-chaos experiment report

## Setup

Seed: 42; runs per cell: 30; recorded runs: 33600.
Faults: empty_output, malformed_output, rate_limit, schema_drift, timeout, transient_error, wrong_value.
Fault rates: 0, 0.1, 0.2, 0.4.
Conditions: ablation: retry, ablation: validation, baseline, resilient, without: redundancy.

## Headline results

| Fault | Rate | Condition | Success (95% Wilson CI) | Silent failure |
|---|---:|---|---:|---:|
| empty_output | 0 | baseline | 100.0% (98.4%–100.0%) | 0.0% |
| empty_output | 0 | resilient | 100.0% (98.4%–100.0%) | 0.0% |
| empty_output | 0.1 | baseline | 78.3% (72.7%–83.1%) | 0.0% |
| empty_output | 0.1 | resilient | 100.0% (98.4%–100.0%) | 0.0% |
| empty_output | 0.2 | baseline | 57.5% (51.2%–63.6%) | 0.0% |
| empty_output | 0.2 | resilient | 99.6% (97.7%–99.9%) | 0.0% |
| empty_output | 0.4 | baseline | 32.9% (27.3%–39.1%) | 0.0% |
| empty_output | 0.4 | resilient | 97.1% (94.1%–98.6%) | 0.0% |
| malformed_output | 0 | baseline | 100.0% (98.4%–100.0%) | 0.0% |
| malformed_output | 0 | resilient | 100.0% (98.4%–100.0%) | 0.0% |
| malformed_output | 0.1 | baseline | 80.4% (74.9%–84.9%) | 0.0% |
| malformed_output | 0.1 | resilient | 100.0% (98.4%–100.0%) | 0.0% |
| malformed_output | 0.2 | baseline | 62.1% (55.8%–68.0%) | 0.0% |
| malformed_output | 0.2 | resilient | 100.0% (98.4%–100.0%) | 0.0% |
| malformed_output | 0.4 | baseline | 31.2% (25.7%–37.4%) | 0.0% |
| malformed_output | 0.4 | resilient | 97.5% (94.7%–98.8%) | 0.0% |
| rate_limit | 0 | baseline | 100.0% (98.4%–100.0%) | 0.0% |
| rate_limit | 0 | resilient | 100.0% (98.4%–100.0%) | 0.0% |
| rate_limit | 0.1 | baseline | 80.8% (75.4%–85.3%) | 0.0% |
| rate_limit | 0.1 | resilient | 99.2% (97.0%–99.8%) | 0.0% |
| rate_limit | 0.2 | baseline | 60.4% (54.1%–66.4%) | 0.0% |
| rate_limit | 0.2 | resilient | 97.1% (94.1%–98.6%) | 0.0% |
| rate_limit | 0.4 | baseline | 33.3% (27.7%–39.5%) | 0.0% |
| rate_limit | 0.4 | resilient | 64.6% (58.3%–70.4%) | 0.0% |
| schema_drift | 0 | baseline | 100.0% (98.4%–100.0%) | 0.0% |
| schema_drift | 0 | resilient | 100.0% (98.4%–100.0%) | 0.0% |
| schema_drift | 0.1 | baseline | 86.7% (81.8%–90.4%) | 0.0% |
| schema_drift | 0.1 | resilient | 100.0% (98.4%–100.0%) | 0.0% |
| schema_drift | 0.2 | baseline | 75.8% (70.0%–80.8%) | 0.0% |
| schema_drift | 0.2 | resilient | 100.0% (98.4%–100.0%) | 0.0% |
| schema_drift | 0.4 | baseline | 52.1% (45.8%–58.3%) | 0.0% |
| schema_drift | 0.4 | resilient | 97.9% (95.2%–99.1%) | 0.0% |
| timeout | 0 | baseline | 100.0% (98.4%–100.0%) | 0.0% |
| timeout | 0 | resilient | 100.0% (98.4%–100.0%) | 0.0% |
| timeout | 0.1 | baseline | 80.0% (74.5%–84.6%) | 0.0% |
| timeout | 0.1 | resilient | 100.0% (98.4%–100.0%) | 0.0% |
| timeout | 0.2 | baseline | 59.2% (52.9%–65.2%) | 0.0% |
| timeout | 0.2 | resilient | 96.2% (93.0%–98.0%) | 0.0% |
| timeout | 0.4 | baseline | 38.8% (32.8%–45.0%) | 0.0% |
| timeout | 0.4 | resilient | 65.0% (58.8%–70.8%) | 0.0% |
| transient_error | 0 | baseline | 100.0% (98.4%–100.0%) | 0.0% |
| transient_error | 0 | resilient | 100.0% (98.4%–100.0%) | 0.0% |
| transient_error | 0.1 | baseline | 77.9% (72.3%–82.7%) | 0.0% |
| transient_error | 0.1 | resilient | 100.0% (98.4%–100.0%) | 0.0% |
| transient_error | 0.2 | baseline | 62.5% (56.2%–68.4%) | 0.0% |
| transient_error | 0.2 | resilient | 97.5% (94.7%–98.8%) | 0.0% |
| transient_error | 0.4 | baseline | 35.8% (30.0%–42.1%) | 0.0% |
| transient_error | 0.4 | resilient | 66.7% (60.5%–72.3%) | 0.0% |
| wrong_value | 0 | baseline | 100.0% (98.4%–100.0%) | 0.0% |
| wrong_value | 0 | resilient | 100.0% (98.4%–100.0%) | 0.0% |
| wrong_value | 0.1 | baseline | 81.7% (76.3%–86.1%) | 18.3% |
| wrong_value | 0.1 | resilient | 95.0% (91.5%–97.1%) | 5.0% |
| wrong_value | 0.2 | baseline | 67.5% (61.3%–73.1%) | 32.5% |
| wrong_value | 0.2 | resilient | 78.8% (73.1%–83.5%) | 21.2% |
| wrong_value | 0.4 | baseline | 37.1% (31.2%–43.4%) | 62.9% |
| wrong_value | 0.4 | resilient | 39.2% (33.2%–45.5%) | 60.8% |

## Ablation results

| Fault | Rate | Condition | Success rate |
|---|---:|---|---:|
| empty_output | 0.2 | ablation: retry | 64.6% |
| empty_output | 0.2 | ablation: validation | 60.4% |
| empty_output | 0.2 | without: redundancy | 99.6% |
| malformed_output | 0.2 | ablation: retry | 61.3% |
| malformed_output | 0.2 | ablation: validation | 67.1% |
| malformed_output | 0.2 | without: redundancy | 100.0% |
| rate_limit | 0.2 | ablation: retry | 99.2% |
| rate_limit | 0.2 | ablation: validation | 56.7% |
| rate_limit | 0.2 | without: redundancy | 99.6% |
| schema_drift | 0.2 | ablation: retry | 73.3% |
| schema_drift | 0.2 | ablation: validation | 60.8% |
| schema_drift | 0.2 | without: redundancy | 100.0% |
| timeout | 0.2 | ablation: retry | 99.6% |
| timeout | 0.2 | ablation: validation | 66.2% |
| timeout | 0.2 | without: redundancy | 99.2% |
| transient_error | 0.2 | ablation: retry | 100.0% |
| transient_error | 0.2 | ablation: validation | 60.4% |
| transient_error | 0.2 | without: redundancy | 99.6% |
| wrong_value | 0.2 | ablation: retry | 61.3% |
| wrong_value | 0.2 | ablation: validation | 60.4% |
| wrong_value | 0.2 | without: redundancy | 57.9% |

## Outcomes by tool

Each run’s task outcome is attributed to every tool used by that task.

| Tool | Condition | Correct | Wrong silent | Failed loud |
|---|---|---:|---:|---:|
| get_distance_km | ablation: retry | 83.5% (2061/2469) | 4.1% (101/2469) | 12.4% (307/2469) |
| get_distance_km | ablation: validation | 70.2% (1677/2390) | 5.1% (121/2390) | 24.8% (592/2390) |
| get_distance_km | baseline | 72.0% (1729/2400) | 4.3% (104/2400) | 23.6% (567/2400) |
| get_distance_km | resilient | 92.3% (2312/2505) | 3.0% (76/2505) | 4.7% (117/2505) |
| get_distance_km | without: redundancy | 94.0% (2364/2516) | 5.0% (125/2516) | 1.1% (27/2516) |
| get_exchange_rate | ablation: retry | 88.6% (3523/3977) | 4.8% (191/3977) | 6.6% (263/3977) |
| get_exchange_rate | ablation: validation | 81.6% (2925/3586) | 5.4% (192/3586) | 13.1% (469/3586) |
| get_exchange_rate | baseline | 81.9% (3004/3669) | 4.6% (169/3669) | 13.5% (496/3669) |
| get_exchange_rate | resilient | 95.1% (3907/4110) | 3.2% (133/4110) | 1.7% (70/4110) |
| get_exchange_rate | without: redundancy | 95.1% (3964/4167) | 4.4% (182/4167) | 0.5% (21/4167) |
| get_fuel_price | ablation: retry | 90.4% (2061/2279) | 4.4% (101/2279) | 5.1% (117/2279) |
| get_fuel_price | ablation: validation | 82.0% (1677/2046) | 5.9% (121/2046) | 12.1% (248/2046) |
| get_fuel_price | baseline | 84.1% (1729/2055) | 5.1% (104/2055) | 10.8% (222/2055) |
| get_fuel_price | resilient | 94.5% (2312/2447) | 3.1% (76/2447) | 2.4% (59/2447) |
| get_fuel_price | without: redundancy | 94.5% (2364/2502) | 5.0% (125/2502) | 0.5% (13/2502) |
| get_price | ablation: retry | 83.0% (4181/5040) | 4.6% (230/5040) | 12.5% (629/5040) |
| get_price | ablation: validation | 68.1% (3430/5040) | 4.7% (239/5040) | 27.2% (1371/5040) |
| get_price | baseline | 69.9% (3525/5040) | 4.2% (211/5040) | 25.9% (1304/5040) |
| get_price | resilient | 92.7% (4671/5040) | 3.3% (165/5040) | 4.0% (204/5040) |
| get_price | without: redundancy | 94.1% (4744/5040) | 4.6% (230/5040) | 1.3% (66/5040) |

## Wrong-value silent failures by tool (rate 0.2)

| Tool | Condition | Silent failures |
|---|---|---:|
| get_distance_km | ablation: retry | 34.4% (31/90) |
| get_distance_km | ablation: validation | 41.1% (37/90) |
| get_distance_km | baseline | 32.2% (29/90) |
| get_distance_km | resilient | 16.7% (15/90) |
| get_distance_km | without: redundancy | 43.3% (39/90) |
| get_exchange_rate | ablation: retry | 41.3% (62/150) |
| get_exchange_rate | ablation: validation | 38.7% (58/150) |
| get_exchange_rate | baseline | 32.7% (49/150) |
| get_exchange_rate | resilient | 24.0% (36/150) |
| get_exchange_rate | without: redundancy | 41.3% (62/150) |
| get_fuel_price | ablation: retry | 34.4% (31/90) |
| get_fuel_price | ablation: validation | 41.1% (37/90) |
| get_fuel_price | baseline | 32.2% (29/90) |
| get_fuel_price | resilient | 16.7% (15/90) |
| get_fuel_price | without: redundancy | 43.3% (39/90) |
| get_price | ablation: retry | 40.0% (72/180) |
| get_price | ablation: validation | 40.0% (72/180) |
| get_price | baseline | 31.7% (57/180) |
| get_price | resilient | 24.4% (44/180) |
| get_price | without: redundancy | 43.9% (79/180) |

## Overhead

| Fault | Rate | Condition | Retry extra calls | Redundancy extra calls | Mean virtual latency (s) |
|---|---:|---|---:|---:|---:|
| empty_output | 0 | ablation: retry | 0.00 | 0.00 | 0.00 |
| empty_output | 0 | ablation: validation | 0.00 | 0.00 | 0.00 |
| empty_output | 0 | baseline | 0.00 | 0.00 | 0.00 |
| empty_output | 0 | resilient | 0.00 | 2.12 | 0.00 |
| empty_output | 0 | without: redundancy | 0.00 | 0.00 | 0.00 |
| empty_output | 0.1 | ablation: retry | 0.00 | 0.00 | 0.00 |
| empty_output | 0.1 | ablation: validation | 0.00 | 0.00 | 0.00 |
| empty_output | 0.1 | baseline | 0.00 | 0.00 | 0.00 |
| empty_output | 0.1 | resilient | 0.04 | 2.55 | 0.01 |
| empty_output | 0.1 | without: redundancy | 0.28 | 0.00 | 0.08 |
| empty_output | 0.2 | ablation: retry | 0.00 | 0.00 | 0.00 |
| empty_output | 0.2 | ablation: validation | 0.00 | 0.00 | 0.00 |
| empty_output | 0.2 | baseline | 0.00 | 0.00 | 0.00 |
| empty_output | 0.2 | resilient | 0.27 | 3.15 | 0.08 |
| empty_output | 0.2 | without: redundancy | 0.62 | 0.00 | 0.19 |
| empty_output | 0.4 | ablation: retry | 0.00 | 0.00 | 0.00 |
| empty_output | 0.4 | ablation: validation | 0.00 | 0.00 | 0.00 |
| empty_output | 0.4 | baseline | 0.00 | 0.00 | 0.00 |
| empty_output | 0.4 | resilient | 1.20 | 4.92 | 0.48 |
| empty_output | 0.4 | without: redundancy | 1.31 | 0.00 | 0.46 |
| malformed_output | 0 | ablation: retry | 0.00 | 0.00 | 0.00 |
| malformed_output | 0 | ablation: validation | 0.00 | 0.00 | 0.00 |
| malformed_output | 0 | baseline | 0.00 | 0.00 | 0.00 |
| malformed_output | 0 | resilient | 0.00 | 2.12 | 0.00 |
| malformed_output | 0 | without: redundancy | 0.00 | 0.00 | 0.00 |
| malformed_output | 0.1 | ablation: retry | 0.00 | 0.00 | 0.00 |
| malformed_output | 0.1 | ablation: validation | 0.00 | 0.00 | 0.00 |
| malformed_output | 0.1 | baseline | 0.00 | 0.00 | 0.00 |
| malformed_output | 0.1 | resilient | 0.05 | 2.60 | 0.02 |
| malformed_output | 0.1 | without: redundancy | 0.29 | 0.00 | 0.08 |
| malformed_output | 0.2 | ablation: retry | 0.00 | 0.00 | 0.00 |
| malformed_output | 0.2 | ablation: validation | 0.00 | 0.00 | 0.00 |
| malformed_output | 0.2 | baseline | 0.00 | 0.00 | 0.00 |
| malformed_output | 0.2 | resilient | 0.28 | 3.20 | 0.09 |
| malformed_output | 0.2 | without: redundancy | 0.50 | 0.00 | 0.18 |
| malformed_output | 0.4 | ablation: retry | 0.00 | 0.00 | 0.00 |
| malformed_output | 0.4 | ablation: validation | 0.00 | 0.00 | 0.00 |
| malformed_output | 0.4 | baseline | 0.00 | 0.00 | 0.00 |
| malformed_output | 0.4 | resilient | 1.00 | 4.72 | 0.36 |
| malformed_output | 0.4 | without: redundancy | 1.36 | 0.00 | 0.57 |
| rate_limit | 0 | ablation: retry | 0.00 | 0.00 | 0.00 |
| rate_limit | 0 | ablation: validation | 0.00 | 0.00 | 0.00 |
| rate_limit | 0 | baseline | 0.00 | 0.00 | 0.00 |
| rate_limit | 0 | resilient | 0.00 | 2.12 | 0.00 |
| rate_limit | 0 | without: redundancy | 0.00 | 0.00 | 0.00 |
| rate_limit | 0.1 | ablation: retry | 0.24 | 0.00 | 0.24 |
| rate_limit | 0.1 | ablation: validation | 0.00 | 0.00 | 0.00 |
| rate_limit | 0.1 | baseline | 0.00 | 0.00 | 0.00 |
| rate_limit | 0.1 | resilient | 0.46 | 2.35 | 0.47 |
| rate_limit | 0.1 | without: redundancy | 0.28 | 0.00 | 0.28 |
| rate_limit | 0.2 | ablation: retry | 0.57 | 0.00 | 0.58 |
| rate_limit | 0.2 | ablation: validation | 0.00 | 0.00 | 0.00 |
| rate_limit | 0.2 | baseline | 0.00 | 0.00 | 0.00 |
| rate_limit | 0.2 | resilient | 1.20 | 2.61 | 1.23 |
| rate_limit | 0.2 | without: redundancy | 0.50 | 0.00 | 0.50 |
| rate_limit | 0.4 | ablation: retry | 1.39 | 0.00 | 1.43 |
| rate_limit | 0.4 | ablation: validation | 0.00 | 0.00 | 0.00 |
| rate_limit | 0.4 | baseline | 0.00 | 0.00 | 0.00 |
| rate_limit | 0.4 | resilient | 2.62 | 2.67 | 2.75 |
| rate_limit | 0.4 | without: redundancy | 1.34 | 0.00 | 1.38 |
| schema_drift | 0 | ablation: retry | 0.00 | 0.00 | 0.00 |
| schema_drift | 0 | ablation: validation | 0.00 | 0.00 | 0.00 |
| schema_drift | 0 | baseline | 0.00 | 0.00 | 0.00 |
| schema_drift | 0 | resilient | 0.00 | 2.12 | 0.00 |
| schema_drift | 0 | without: redundancy | 0.00 | 0.00 | 0.00 |
| schema_drift | 0.1 | ablation: retry | 0.00 | 0.00 | 0.00 |
| schema_drift | 0.1 | ablation: validation | 0.00 | 0.00 | 0.00 |
| schema_drift | 0.1 | baseline | 0.00 | 0.00 | 0.00 |
| schema_drift | 0.1 | resilient | 0.05 | 2.58 | 0.01 |
| schema_drift | 0.1 | without: redundancy | 0.21 | 0.00 | 0.05 |
| schema_drift | 0.2 | ablation: retry | 0.00 | 0.00 | 0.00 |
| schema_drift | 0.2 | ablation: validation | 0.00 | 0.00 | 0.00 |
| schema_drift | 0.2 | baseline | 0.00 | 0.00 | 0.00 |
| schema_drift | 0.2 | resilient | 0.21 | 3.14 | 0.05 |
| schema_drift | 0.2 | without: redundancy | 0.41 | 0.00 | 0.13 |
| schema_drift | 0.4 | ablation: retry | 0.00 | 0.00 | 0.00 |
| schema_drift | 0.4 | ablation: validation | 0.00 | 0.00 | 0.00 |
| schema_drift | 0.4 | baseline | 0.00 | 0.00 | 0.00 |
| schema_drift | 0.4 | resilient | 0.97 | 4.50 | 0.32 |
| schema_drift | 0.4 | without: redundancy | 1.18 | 0.00 | 0.44 |
| timeout | 0 | ablation: retry | 0.00 | 0.00 | 0.00 |
| timeout | 0 | ablation: validation | 0.00 | 0.00 | 0.00 |
| timeout | 0 | baseline | 0.00 | 0.00 | 0.00 |
| timeout | 0 | resilient | 0.00 | 2.12 | 0.00 |
| timeout | 0 | without: redundancy | 0.00 | 0.00 | 0.00 |
| timeout | 0.1 | ablation: retry | 0.26 | 0.00 | 1.63 |
| timeout | 0.1 | ablation: validation | 0.00 | 0.00 | 1.45 |
| timeout | 0.1 | baseline | 0.00 | 0.00 | 1.20 |
| timeout | 0.1 | resilient | 0.51 | 2.35 | 3.25 |
| timeout | 0.1 | without: redundancy | 0.29 | 0.00 | 1.81 |
| timeout | 0.2 | ablation: retry | 0.48 | 0.00 | 3.05 |
| timeout | 0.2 | ablation: validation | 0.00 | 0.00 | 2.02 |
| timeout | 0.2 | baseline | 0.00 | 0.00 | 2.45 |
| timeout | 0.2 | resilient | 1.13 | 2.56 | 7.44 |
| timeout | 0.2 | without: redundancy | 0.49 | 0.00 | 3.14 |
| timeout | 0.4 | ablation: retry | 1.22 | 0.00 | 7.96 |
| timeout | 0.4 | ablation: validation | 0.00 | 0.00 | 3.90 |
| timeout | 0.4 | baseline | 0.00 | 0.00 | 3.67 |
| timeout | 0.4 | resilient | 2.62 | 2.58 | 19.07 |
| timeout | 0.4 | without: redundancy | 1.28 | 0.00 | 8.54 |
| transient_error | 0 | ablation: retry | 0.00 | 0.00 | 0.00 |
| transient_error | 0 | ablation: validation | 0.00 | 0.00 | 0.00 |
| transient_error | 0 | baseline | 0.00 | 0.00 | 0.00 |
| transient_error | 0 | resilient | 0.00 | 2.12 | 0.00 |
| transient_error | 0 | without: redundancy | 0.00 | 0.00 | 0.00 |
| transient_error | 0.1 | ablation: retry | 0.22 | 0.00 | 0.07 |
| transient_error | 0.1 | ablation: validation | 0.00 | 0.00 | 0.00 |
| transient_error | 0.1 | baseline | 0.00 | 0.00 | 0.00 |
| transient_error | 0.1 | resilient | 0.51 | 2.33 | 0.14 |
| transient_error | 0.1 | without: redundancy | 0.23 | 0.00 | 0.07 |
| transient_error | 0.2 | ablation: retry | 0.54 | 0.00 | 0.18 |
| transient_error | 0.2 | ablation: validation | 0.00 | 0.00 | 0.00 |
| transient_error | 0.2 | baseline | 0.00 | 0.00 | 0.00 |
| transient_error | 0.2 | resilient | 1.07 | 2.57 | 0.42 |
| transient_error | 0.2 | without: redundancy | 0.54 | 0.00 | 0.15 |
| transient_error | 0.4 | ablation: retry | 1.26 | 0.00 | 0.44 |
| transient_error | 0.4 | ablation: validation | 0.00 | 0.00 | 0.00 |
| transient_error | 0.4 | baseline | 0.00 | 0.00 | 0.00 |
| transient_error | 0.4 | resilient | 2.53 | 2.51 | 1.21 |
| transient_error | 0.4 | without: redundancy | 1.22 | 0.00 | 0.45 |
| wrong_value | 0 | ablation: retry | 0.00 | 0.00 | 0.00 |
| wrong_value | 0 | ablation: validation | 0.00 | 0.00 | 0.00 |
| wrong_value | 0 | baseline | 0.00 | 0.00 | 0.00 |
| wrong_value | 0 | resilient | 0.00 | 2.12 | 0.00 |
| wrong_value | 0 | without: redundancy | 0.00 | 0.00 | 0.00 |
| wrong_value | 0.1 | ablation: retry | 0.00 | 0.00 | 0.00 |
| wrong_value | 0.1 | ablation: validation | 0.00 | 0.00 | 0.00 |
| wrong_value | 0.1 | baseline | 0.00 | 0.00 | 0.00 |
| wrong_value | 0.1 | resilient | 0.00 | 2.44 | 0.00 |
| wrong_value | 0.1 | without: redundancy | 0.00 | 0.00 | 0.00 |
| wrong_value | 0.2 | ablation: retry | 0.00 | 0.00 | 0.00 |
| wrong_value | 0.2 | ablation: validation | 0.00 | 0.00 | 0.00 |
| wrong_value | 0.2 | baseline | 0.00 | 0.00 | 0.00 |
| wrong_value | 0.2 | resilient | 0.00 | 2.84 | 0.00 |
| wrong_value | 0.2 | without: redundancy | 0.00 | 0.00 | 0.00 |
| wrong_value | 0.4 | ablation: retry | 0.00 | 0.00 | 0.00 |
| wrong_value | 0.4 | ablation: validation | 0.00 | 0.00 | 0.00 |
| wrong_value | 0.4 | baseline | 0.00 | 0.00 | 0.00 |
| wrong_value | 0.4 | resilient | 0.00 | 3.17 | 0.00 |
| wrong_value | 0.4 | without: redundancy | 0.00 | 0.00 | 0.00 |

## What did not work

- `wrong_value`: resilient success 78.8%; silent failures 21.2%. The measured improvement is not clearly separated from baseline or silent failures exceed 5%.

## Charts

![Success curves](charts/degradation_curves.png)

![Outcome mix](charts/outcomes_stacked.png)

![Ablation heatmap](charts/ablation_heatmap.png)
