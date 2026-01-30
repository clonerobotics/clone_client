from __future__ import annotations

import mujoco as mj

from clone_client.dipole_estimation.mujoco_utils import build_joint_models_from_mujoco


class MuJoCoBackend:
    def __init__(self, model_xml_path: str, *, enable_viewer: bool = False) -> None:
        self.m = mj.MjModel.from_xml_path(model_xml_path)
        self.d = mj.MjData(self.m)
        mj.mj_forward(self.m, self.d)

        self._running = True
        self._viewer = None

        if enable_viewer:
            import mujoco.viewer  # local import to avoid any UI deps when disabled

            self._viewer = mujoco.viewer.launch_passive(self.m, self.d)
            self._running = self._viewer.is_running()

    def apply_controls(self, joint_name_to_value: dict[str, float]) -> None:
        for jname, val in joint_name_to_value.items():
            try:
                self.d.joint(jname).qpos = val
            except Exception:
                j_id = mj.mj_name2id(self.m, mj.mjtObj.mjOBJ_JOINT, jname)
                if j_id < 0:
                    raise KeyError(f"joint '{jname}' not found")
                qpos_adr = self.m.jnt_qposadr[j_id]
                self.d.qpos[qpos_adr] = val

    def forward(self) -> None:
        mj.mj_forward(self.m, self.d)

        if self._viewer is None:
            return

        if self._viewer.is_running():
            self._viewer.sync()
            self._viewer.user_scn.ngeom = 0
        else:
            self._running = False

    def build_joint_models(self, cfg):
        return build_joint_models_from_mujoco(self.m, self.d, cfg)

    def is_running(self) -> bool:
        if self._viewer is None:
            return self._running
        return self._viewer.is_running()
