# Dipole Estimation (Python) — Scripts & Workflow

This directory contains Python utilities used to:
1) Parse a hand/joint mapping config (TOML preferred),
2) Build a joint model set from a MuJoCo XML,
3) Export the generated model set to disk,
4) Validate exported artifacts,
5) Use the model set online to convert telemetry pose quaternions into joint angles.

The overall pipeline is:

```
TOML joint config + MuJoCo XML
            |
            v
    generate_joint_models.py
            |
            v
   joint_models.{toml|json}
            |
            v
   validate_joint_models.py
            |
            v
 runtime usage (telemetry -> angles)
```

---

## Requirements

- Python 3.11+
- `numpy`
- `scipy`
- `mujoco`

---

## Configuration Format (TOML)

Config describes which joints to process and where the sensor/magnet sites are in MuJoCo.

Example:

```toml
[[joints]]
name = "r-wrist-first"
control_bindings = [
  { z = "Joint__z_carpal_row_1z_armature_r" },
  { y = "Joint__y_carpal_row_1y_armature_r" },
]

[joints.sites]
sensor_site = "Site__center__magnetometers_wrist_r__..."
magnet_site = "Site__magnet__magnetometers_wrist_r__..."

[joints.sensor_mapping]
clone_sensor_id = "0x7d"
sensor_magnet_inversion = true
magnet_local_axis = [0, 0, 1]
```

### `r_corr` convention
`r_corr` is **always present** in `SensorMapping`. If omitted in the config, it is defaulted during parsing to:

- 180° rotation around Y axis (`Ry(pi)`):
  ```
  [-1, 0,  0]
  [ 0, 1,  0]
  [ 0, 0, -1]
  ```

---

## Scripts

### 1) Generate joint model set from MuJoCo

**Purpose:** Load the TOML config + MuJoCo XML and generate `JointModelInfo` on disk.

Typical file name:
- `generate_joint_models.py`

Usage:

```bash
python -m clone_client.dipole_estimation.generate_joint_models \
  --config hand_mapping_config_right.toml \
  --model-xml /path/to/hand_r.xml \
  --out joint_models.toml \
  --format toml
```

Arguments:
- `--config`: TOML joint mapping config.
- `--model-xml`: MuJoCo XML path.
- `--out`: output file path.
- `--format`: `toml` (preferred) or `json`.

Notes:
- The generator should **fail fast** on missing MuJoCo names:
  - unknown `sensor_site` / `magnet_site`
  - unknown MuJoCo joint names referenced by `control_bindings`


---

### 2) Validate a joint model set

**Purpose:** Sanity-check numeric correctness and required structure.

Typical file name:
- `validate_joint_models.py`

Usage:

```bash
python -m clone_client.dipole_estimation.validate_joint_models joint_models.toml
# or
python -m clone_client.dipole_estimation.validate_joint_models joint_models.json
```

Checks include:
- `Mat3` / rotations:
  - finite values
  - orthonormal columns
  - determinant ≈ +1
- vectors:
  - finite
  - expected shapes
  - expected unit length for axis-like fields:
    - `dipole.direction`
    - `magnet.base_z_in_sensor`
    - `mapping.magnet_local_axis`

Exit codes:
- `0`: OK
- `1`: validation failed

---

### 3) Telemetry to joint angles (runtime usage)

**Purpose:** Convert telemetry pose estimation quaternions into control angles using joint models.

Typical entry points:
- `dipole_estimator_usage.py` (example)
- conversion module (`pose_msg_to_control_angles`)

High-level flow:
1) Fetch `JointModelInfo` from system info (protobuf) or load from disk.
2) Convert `PoseEstimationData.pose_estimation` quaternions into `Rotation`s per frame.
3) Apply `control_bindings` to map frame Euler axes into named controls.

Example pattern (pseudocode):

```py
system_info = await client.state_store.get_system_info()
joint_models = JointModelInfo.from_proto(system_info.joint_models)

angles = pose_msg_to_control_angles(tele.pose_estimation, joint_models.items)
```

---

## Outputs

### JointModelInfo (TOML/JSON)

Root:
- `items`: map of `joint_name -> JointModel`

A `JointModel` includes:
- `joint_frames.items`: per-frame `{ name -> { R_wJ, origin_w } }`
- `sensor`: `{ frame_wS, origin_w }`
- `magnet`: `{ origin_w, base_z_in_sensor }`
- `dipole`: `{ position, direction }`
- `mapping`: `{ clone_sensor_id, magnet_local_axis, sensor_magnet_inversion, r_corr }`
- `control_bindings`: list of axis→hinge/control mappings

---

## Common Failure Modes

### Empty or near-empty output file
Usually caused by:
- `mj_name2id(..., SITE, sensor_site)` returning `-1`
- `mj_name2id(..., SITE, magnet_site)` returning `-1`
- joint names in `control_bindings` not existing in the MuJoCo model

Fix:
- Validate all MuJoCo names; fail fast in generation.
- Add debug prints for `sid/mid` and joint ids.

### Rotation validation failures
- `r_corr` or any stored `Mat3` not orthonormal / det not +1
- upstream numeric issues in frame construction

Fix:
- ensure frame construction always produces a right-handed basis
- normalize and re-orthogonalize if needed

---

## Pose key naming

Pose outputs are keyed by a stable string identifier referred to as the *pose key*.
The canonical pose key format is:

- `"<joint_name>::<frame_name>"`

Where:
- `joint_name` is the joint identifier (key under `JointModelInfoFile.joints` / MuJoCo cfg).
- `frame_name` is the joint-frame identifier (key under `joints.<joint_name>.joint_frames.frames`).

Example:
- statics path: `joints.l-thumb-pip.joint_frames.frames.l-thumb-pip_frame0`
- pose key:     `"l-thumb-pip::l-thumb-pip_frame0"`

Some downstream tooling may accept a shorthand `"joint"` form as `(joint, joint)`,
but this only works if a frame named exactly `joint_name` exists. MuJoCo-built joint
models typically name frames as `"{joint}_frame{idx}"`, so consumers should prefer
the canonical `"joint::frame"` form.

---
## Development Notes

- Prefer `dict`, `list`, `tuple`, and `T | None` types (Python 3.10+).
- Avoid silent fallbacks during generation; generation should be strict.
- Prefer TOML for configs and outputs; JSON remains supported for interop/debugging.
- Keep the “model info” format stable; changes to the proto schema should be mirrored in:
  - `JointModelInfo.from_proto(...)` / `.to_proto(...)` shims
  - validators
  - generator output format
