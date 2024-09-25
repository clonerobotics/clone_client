# Clone API client for the Clone Robot

[Website](http://clonerobotics.com) | [Code examples](/clone_client/examples/)

The Clone client package offers high-level API to directly control the Clone Robot. Current repository version contains already built version of the package, development is done outside GitHub and for that reasons we do not accept pull requests, however we are open for any suggestions and bug reports using the issue tracking system.

**`⚠ Package In Development`**

This repository is in pre-beta, prone to drastic changes in the future, so please be aware of this. We will be slowly migrating development onto GitHub with the full introduction of releases and pull requests.

We use GitHub tagging mechanism for each update of the package for convenience.

> **Note**: This API client uses **asyncio** to run the client asynchronously, which means any integration with this package requires to be compatible with this paradigm. If you are looking for a simplified, synchronous version of the API client, please see this wrapper: https://github.com/clonerobotics/clone_client_sync

## Requirements

Obviously you're gonna need the Clone Robot to use this package. Please contact us if you want to include our product in your research.

The package requires Python >= `3.10`, < `4.0`.

## Installation

Unfortunately, we do not provide PyPI releases just yet, but you can use this repository as an installation candidate using pip:

[https://pip.pypa.io/en/stable/cli/pip_install/#examples](https://pip.pypa.io/en/stable/cli/pip_install/#examples)

## Usage

### Getting started

To start using this package with a version of the hardware, you're gonna need a unique name provided along with the Clone Robot..

```python
from clone_client.client import Client

async def entrypoint():
    async with Client("robot") as client:
        ...
```

you can also use address in the network directly:

```python
from clone_client.client import Client

async def entrypoint():
    async with Client(address="192.168.1.10") as client:
        ...
```

If you want more information about what is happening during initialization process (helpful for debugging) we recommend setting up `logging` module to `INFO` or `DEBUG` level.

### Using controller

The controller is a simple communication interface that allows you to send commands to the robot. It mostly controls muscles and water pump (pressure source).

> **Note:** For some versions of the robot the water pump might not be available due to external pressure source. In those cases the pump API would raise an exception.

```python
from clone_client.client import Client

async def entrypoint():
    async with Client("robot") as client:
        # Start the waterpump and wait for it to reach desired pressure
        await client.start_waterpump()
        await client.wait_for_desired_pressure()

        # Send pressures instructions for each muscle
        data = [0 for _ in range(client.number_of_muscles)]
        await client.set_pressures(data)
```

`set_pressures` function accepts a sequence of floats and each value represents a normalized pressure instruction for a single muscle.

The value range is normalized to `[0, 1]`. To get information about what is the maxiumum pressure achievable for each muscle, you can use a following script:

```python
async def entrypoint():
    async with Client("robot") as client:
        sinfo = await client.get_system_info()

        # e.g. checking the calibration range for the first muscle
        # Values are presented in milibars, negative values are
        # a normal feedback from the pressure sensor due to noise
        m_min = sinfo.calibration.pressure_sensors[0].min
        m_max = sinfo.calibration.pressure_sensors[0].max

        print(f"Muscle 0: min={m_min}, max={m_max}")
```

Setting the pressure is also achievable using stream. This offer the same functionality but in a bit more robust and more performant way due to limited numbers of request / response cycles.

```python

async def entrypoint():
    async with Client("robot") as client:
        async def generator():
            pressures = [0] * client.number_of_muscles
            while 1:
                yield pressures

       await client.stream_set_pressures(generator())
```

See the [stream example](./clone_client/examples/using_data_streams.py) for more information about how to use the stream.

> **Note**: We do not limit the control frequency internally, however there are hardware limitations that might prevent you from setting the pressure too fast.

Recommended control frequency for our development products can be calculated as:

- **hard** cap: `10000 / (no_muscles * 1.5)` (166Hz for Clone Hand)
- **soft** cap: `10000 / (no_muscles * 1.25)` (200Hz for Clone Hand)

We are aware of these limitations and are working on hardware changes to allow for much higher control frequency.

We offer a utility context manager that ensures very precise ticks, see:
[clone_client.utils](./clone_client/utils.py):

```python
from clone_client.client import Client
from clone_client.utils import async_busy_ticker

async def entrypoint():
    async with Client("robot") as client:
        while True:
            async with async_busy_ticker(1 / 100):
                await client.set_pressures([0.2] * client.number_of_muscles)
```

> **Warning**: We do not limit the number of concurrent muscle actuations. Setting pressures must be use with caution to ensure the safety of the hardware (to avoid too much tension / strains on the bone / joint). For initial experiments limit the number of actuated muscles or operate on lower values (such as 0.2 - 0.3).

On top of pressure controller the client implements a various way to control muscles such as timed impulses and oscilations. See the [implementations](./clone_client/client.py) for more information.

### Reading feedback data

Clone Robot is equipped with a set of sensors that allow you to read current pressure in each muscle and the IMU data (beta). You can also check the current and desired (target) pressure of the water pump.

```python
from clone_client.client import Client

async def entrypoint():
    async with Client("robot") as client:
        # Start the water pump and wait for it to reach desired pressure
        await client.start_waterpump()
        await client.wait_for_desired_pressure()

        # Get current information about water pump
        waterpump_info = await client.get_waterpump_info()

        # Whether or not water pump controller is running
        print("Is running", waterpump_info.is_running)

        # Current pressure in the water pump
        print("Current pressure", waterpump_info.pressure)

        # Desired pressure in the water pump
        print("Desired pressure", waterpump_info.desired_pressure)

        # Get current telemetry in the muscles
        telemetry = await client.get_telemetry()
        print("Pressurs ", telemetry.pressures)
        print("IMU ", telemetry.imu)
```

Mind that IMU data is still in beta and might not be available for all versions of the hardware.

Receiving feedback data is also available using subscription. This offer the same functionality but it's hooked directly into the internal feedback loop offering always up-to-date data.

```python
from clone_client.client import Client

async def entrypoint():
    async with Client("robot") as client:
        async for telemetry in client.subscribe_telemetry():
            print("Pressures ", telemetry.pressures)
            print("IMU ", telemetry.imu)
```

Example code can be found in the [examples](./clone_client/examples) directory.

### Data ordering

Both `set_pressures` (or `stream_set_pressures`) and `get_pressures` (or `subscribe_telemetry`) functions are based on the data in the same order as the muscles are connected to the controller. It is important to preserve the ordering of sent data to avoid any problems with the hardware or/and your own software.

To get the current order of the muscles, you can can use `muscle_order` property of the client.

We also provide utils to get the name of the specific muscle based on its index and vice versa.

```python
from clone_client.client import Client

async def entrypoint():
    async with Client("robot") as client:
        # Get the muscle order
        muscle_order = client.muscle_order

        # Get the name of the muscle with index 0
        muscle_name = client.muscle_name(0)

        # Get the index of the muscle with name "muscle_0"
        muscle_index = client.muscle_index("muscle_0")
```

It is recommended to save the muscle order in your application and in case of any changes in the hardware you can verify whether or not the order is still the same to avoid potential problems in e.g. training a custom NN model.

## API Reference

### client

Please check the [source code](./clone_client/client.py) and [examples](./clone_client/examples/) for more information about the API. We try to provide detailed docstrings and typings for each function and class with comments in more complex parts of the code.

For all-in-one explanation please see [this file](./clone_client/examples/api_explanation.py)

### error_frames

[clone_client.error_frames](./clone_client/error_frames.py)

Contains all errors that can occurr during the execution of any function of the `Client` related to networking. See docstrings for more information about when each error can occurr.

### exceptions

[clone_client.exceptions](./clone_client/exceptions.py)

Contains all exceptions that can occurr during the execution of any function of the `Client`. See docstrings for more information about when each exception can occurr.

Overall we try to keep typings and docstrings up to date so you can always check the source code for more information about the package.

## Contributing

We are open for any suggestions and bug reports using issue system, however we do not accept pull requests at the moment.

In case of any problem please contact us at [https://clonerobotics.com/contact](https://clonerobotics.com/contact).
