"""Some utils purely for prototyping, e.g. parsing kinematic chains and organizing
data in those chains.
"""

import logging
from typing import Annotated

import numpy as np
from scipy.spatial.transform import Rotation

from clone_client.client import Client
from clone_client.state_store.proto.state_store_pb2 import IMUData, ImuMappingModel

L = logging.getLogger(__name__)

Quaternion = Annotated[np.ndarray[tuple[4], np.dtype[np.float32]], "Scalar last"]


class FloatPrinter(float):
    def __repr__(self) -> str:
        return f"{self: .3f}"


async def get_imu_nodes_dict(client: Client) -> dict[int, ImuMappingModel]:
    L.debug("Getting system info")
    imus_mapping = {item.node_id: item for item in (await client.get_system_info()).imus}
    return imus_mapping


def rot_from_imu_data(imu_data: IMUData) -> Rotation:
    return Rotation.from_quat([imu_data.x, imu_data.y, imu_data.z, imu_data.w])


def quat_from_imu_data(imu_data: IMUData) -> Quaternion:
    return np.array([imu_data.x, imu_data.y, imu_data.z, imu_data.w])


def rot_relative_extrinsic(from_rot: Rotation, to_rot: Rotation) -> Rotation:
    return to_rot * from_rot.inv()


def rot_relative_intrinsic(from_rot: Rotation, to_rot: Rotation) -> Rotation:
    return from_rot.inv() * to_rot
