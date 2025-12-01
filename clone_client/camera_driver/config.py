from pydantic_settings import BaseSettings

from clone_client.config import ClientConfig


class CameraDriverClientConfig(BaseSettings, ClientConfig):
    """Cmamera Driver client configuration."""

    # pylint: disable=too-few-public-methods

    class Config:
        # pylint: disable=too-few-public-methods, missing-class-docstring
        env_prefix = "CAMERA_CLIENT_"

    grpc_addr: str = "127.0.0.1:8080"
