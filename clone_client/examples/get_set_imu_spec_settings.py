import asyncio
from pprint import pprint

from clone_client.client import Client
from clone_client.proto.hardware_driver_pb2 import IMUSpecSettingsMessage


async def main() -> None:
    async with Client(address="127.0.0.1", tunnels_used=Client.TunnelsUsed.HW_DRIVER) as client:
        print("client connected")
        settings = {
            0x41: IMUSpecSettingsMessage.IMUSpecSettings(
                should_write=True,
                trust_factors=IMUSpecSettingsMessage.IMUSpecSettings.TrustFactors(
                    acc=1.0, mag=2.0, acc_external=3.0
                ),
                bias_thresholds=IMUSpecSettingsMessage.IMUSpecSettings.GyroBiasThresholds(
                    acc=4.0, gyr=5.0, mag=6.0
                ),
                learning_mode=IMUSpecSettingsMessage.IMUSpecSettings.LearningMode.Dynamic,
                options=IMUSpecSettingsMessage.IMUSpecSettings.Options(
                    use_gyro_temperature_calibration=True,
                    use_acc_calibration=False,
                    use_mag_calibration=True,
                    enable_continuous_mag_calibration=False,
                    store_bias_and_calibration_periodically=False,
                    enable_magnetometer_magnitude_gating=False,
                    enable_magnetometer_alignment_gating=True,
                ),
            )
        }
        print("settings out:")
        pprint(settings)
        await client.hw_driver.set_imu_spec_settings(settings)
        imu_spec_settings = await client.hw_driver.get_imu_spec_settings()
        print("settings in:")
        pprint(imu_spec_settings[0x41])
        print("all settings in:")
        pprint(imu_spec_settings)


asyncio.run(main())
