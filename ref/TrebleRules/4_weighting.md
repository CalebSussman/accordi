# Phase IV: Weighting, Tuning & Physical Constants

**Artifact Type:** Configuration / Mathematical Definition
**Engine Version:** 4.3 (Final Approved)
**Description:** Defines the mathematical cost function and specific hyperparameter values for the A* search.
**Unit Standard:** **NMU (Normalized Movement Units)**, where $1.0 \text{ NMU} \approx 1.0 \text{ mm}$ of comfortable lateral hand displacement.

---

## 1. The Cost Function (Mathematical Definition)

The total cost $f(n)$ for a transition between state $S_{prev}$ and $S_{curr}$ is defined mathematically below.

### A. Total Cost Aggregation
$$Cost_{total} = (C_{movement} \times M_{technique}) + \sum P_{ergonomic}$$

### B. Movement Cost ($C_{movement}$)
Represents the physical work to move the hand centroid.
$$C_{movement} = (d_{euclidean} \times W_{dist}) + (|\Delta_{row}| \times W_{row})$$

### C. Technique Multipliers ($M_{technique}$)
Applied to the movement cost **before** adding ergonomic penalties.
$$M_{technique} = M_{pivot} \times M_{bellows}$$

### D. Ergonomic Penalties ($P_{ergonomic}$)
These are additive costs.
$$P_{ergonomic} = P_{cross} + P_{weak} + P_{sub} + P_{interval}$$

#### 1. Crossing Logic ($P_{cross}$)
**Mapping Rule:** Given two crossing fingers $f_A$ and $f_B$ where $f_A < f_B$ (e.g., 1 and 3):
1.  **Under-Crossing:** If thumb/lower finger moves "inside" the hand context. Key format: `"{fA}_under_{fB}"`.
2.  **Over-Crossing:** If higher finger moves over lower. Key format: `"{fB}_over_{fA}"`.
3.  **Fallback:** If the specific key is not found in the JSON `crossing_lookup`, use `generic_weak_crossing`.

$$P_{cross} = \text{Lookup}(Key_{crossing})$$

#### 2. Weakness & Stress ($P_{weak}$)
Combines static finger weakness with metric stress (downbeats).
$$P_{weak} = \sum_{f \in ActiveFingers} (P_{static}(f) + (IsDownbeat ? P_{stress\_bias} : 0))$$

#### 3. Substitution ($P_{sub}$)
Differentiates between easy adjacent swaps and risky jumps.
$$P_{sub} = \begin{cases} 
P_{sub\_adj} & \text{if } |f_{new} - f_{old}| = 1 \\
P_{sub\_cross} & \text{if } |f_{new} - f_{old}| > 1 
\end{cases}$$

#### 4. Interval Reach ($P_{interval}$)
Penalizes spans that approach the physical limit.
$$P_{interval} = \begin{cases} 
(Span_{mm} - Thresh_{mm}) \times Slope & \text{if } Span_{mm} > Thresh_{mm} \\
0 & \text{otherwise}
\end{cases}$$

---

## 2. Configuration & Weights (JSON)

This JSON object is the single source of truth for the engine.

```json
{
  "engine_config_id": "bayan_v4_standard",
  "physics_constants": {
    "description": "Physical dimensions of Tula/Jupiter B-System Bayan (Millimeters)",
    "row_spacing_mm": 19.5,
    "col_spacing_mm": 16.0,
    "button_diameter_mm": 15.0,
    "hand_geometry": {
      "max_span_mm": 165.0,
      "max_adjacent_spread_mm": 60.0
    }
  },
  "cost_weights": {
    "description": "Coefficients for the cost function (Normalized Movement Units)",
    "movement": {
      "weight_distance_per_mm": 1.0,
      "weight_row_jump": 1.5
    },
    "multipliers": {
      "pivot_reduction_factor": 0.6,
      "bellows_reduction_factor": 0.5
    },
    "penalties": {
      "crossing_lookup": {
        "description": "Costs for geometric inversions. Keys derived via Mapping Rule.",
        "1_under_2": 5.0,
        "1_under_3": 15.0,
        "1_under_4": 40.0,
        "1_under_5": 90.0,
        "3_over_4": 80.0,
        "4_over_5": 100.0,
        "generic_weak_crossing": 80.0
      },
      "finger_static_weakness": {
        "description": "Base cost for using specific fingers (1=Thumb, 5=Pinky)",
        "1": 0.0,
        "2": 0.0,
        "3": 0.1,
        "4": 0.8,
        "5": 0.4
      },
      "metric_stress_bias": 10.0,
      "substitution": {
        "adjacent": 4.0,
        "cross_hand": 25.0
      },
      "interval_reach": {
        "threshold_mm": 140.0,
        "slope": 2.0
      }
    }
  }
}
```

---

## 3. Tuning Profiles (Overrides)

Apply these patches to the default configuration to alter engine behavior.

### Profile A: "Conservatory Student" (Strict/Safe)

*   **Logic:** Penalizes risk heavily. Substitution is only allowed if adjacent. Row jumps are discouraged.

```json
{
  "profile_id": "conservatory_safe",
  "overrides": {
    "cost_weights": {
      "movement": {
        "weight_row_jump": 3.0
      },
      "penalties": {
        "crossing_lookup": {
          "3_over_4": 200.0,
          "generic_weak_crossing": 200.0
        },
        "substitution": {
          "cross_hand": 100.0
        },
        "finger_static_weakness": {
          "4": 2.0,
          "5": 1.5
        }
      }
    }
  }
}
```

### Profile B: "Virtuoso" (Efficiency/Speed)

*   **Logic:** Prioritizes distance minimization. High tolerance for crossings and row jumps if it saves travel time.

```json
{
  "profile_id": "virtuoso_speed",
  "overrides": {
    "physics_constants": {
      "hand_geometry": {
        "max_span_mm": 180.0
      }
    },
    "cost_weights": {
      "movement": {
        "weight_row_jump": 0.8
      },
      "penalties": {
        "crossing_lookup": {
          "3_over_4": 40.0
        },
        "metric_stress_bias": 0.0,
        "substitution": {
          "cross_hand": 15.0
        }
      }
    }
  }
}
```