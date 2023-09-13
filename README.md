# Clone API client for the Hand

[Website](http://clonerobotics.com) | [Code examples](/clone_client/examples)

The Clone client package offers high-level API to directly control the Clone Hand. Current repository version contains already built version of the package, development is done outside GitHub and for that reasons we do not accept pull requests, however we are open for any suggestions and bug reports using the issue tracking system.

**`⚠ Package In Development`**

This repository is in pre-beta, prone to drastic changes in the future, so please be aware of this. We will be slowly migrating development onto GitHub with the full introduction of releases and pull requests.

We use GitHub tagging mechanism for each update of the package for convenience.

## Requirements

Obviously you're gonna need the Clone Hand to use this package. Please contact us if you want to include our product in your research.

The package requires Python 3.9.
We are working to make it compatible with Python 3.10 and 3.11.

## Installation

Unfortunately, we do not provide PyPI releases just yet, but you can use this repository as an installation candidate using pip:

[https://pip.pypa.io/en/stable/cli/pip_install/#examples](https://pip.pypa.io/en/stable/cli/pip_install/#examples)

## Usage

### Getting started

To start using this package with a version of the hardware, you're gonna need a unique name provided along with the Clone Hand..

```python
from clone_client.client import Client

async def entrypoint():
    async with Client("hand_name") as client:
        ...
```

If you want more information about what is happening during initialization process (helpful for debugging) we recommend setting up `logging` module to `INFO` or `DEBUG` level.

### Using controller

The controller is a simple communication interface that allows you to send commands to the hand. It mostly controls muscles and pressuregen.

```python
from clone_client.client import Client

async def entrypoint():
    async with Client("hand_name") as client:
        # Start the pressuregen and wait for it to reach desired pressure
        client.start_pressuregen()
        client.wait_for_desired_pressure()

        # Send muscles instructions
        data = [-1 for _ in range(client.number_of_muscles)]
        client.set_muscles(data)
```

`set_muscles` function accepts a sequence of floats however current version only cares whether or not a value is less than 0, greater than 0 or equal 0, meaning you can limit the instruction set to 3 values: -1, 0 and 1.

This range might change in the future for more sophisticated and easier control.

Each value corresponds to different behaviour:

- `-1`: pressure in the muscle is decreasing as long as this value is being sent
- `0`: pressure doesn't increase or decreaase, it keeps the pressure constant ("locks" the valve)
- `1`: pressure in the muscle is increasing as long as this value is being sent

It is encouraged to keep sending the same values in a constant loop and stop sending (or keep sending zeros) if the pressure readings are satisfactory. Due to safety reasons, if a hand controller doesn't receive any value for more than 10ms, it automatically locks the valve of the muscle (equivalent of sending `0`).

### Reading feedback data

Clone Hand is equipped with a set of sensors that allow you to read current pressure in each muscle. You can also check the current and desired (target) pressure of the pressuregen.

```python
from clone_client.client import Client

async def entrypoint():
    async with Client("hand_name") as client:
        # Start the pressuregen and wait for it to reach desired pressure
        client.start_pressuregen()
        client.wait_for_desired_pressure()

        # Get current information about pressuregen
        pressuregen_info = client.get_pressuregen_info()

        # Whether or not pressuregen controller is running
        print("Is running", pressuregen_info.is_running)

        # Current pressure in the pressuregen
        print("Current pressure", pressuregen_info.pressure)

        # Desired pressure in the pressuregen
        print("Desired pressure", pressuregen_info.desired_pressure)

        # Get current pressure in the muscles
        pressures = client.get_pressures()
```

Example code can be found in the [examples](./clone_client/examples) directory.

### Data ordering

Both `set_muscles` and `get_pressures` functions are based on the data in the same order as the muscles are connected to the controller. It is important to preserve the ordering of sent data to avoid any problems with the hardware or/and your own software.

To get the current order of the muscles, you can can use `muscle_order` property of the client.

We also provide utils to get the name of the specific muscle based on its index and vice versa.

```python
from clone_client.client import Client

async def entrypoint():
    async with Client("hand_name") as client:
        # Get the muscle order
        muscle_order = client.muscle_order

        # Get the name of the muscle with index 0
        muscle_name = client.muscle_name(0)

        # Get the index of the muscle with name "muscle_0"
        muscle_index = client.muscle_index("muscle_0")
```

It is recommended to save the muscle order in your application and in case of any changes in the hardware you can verify whether or not the order is still the same to avoid potential problems in e.g. training a custom NN model.

## API Reference

Below, you can find the API reference for the package, along with a broad explanation of its main functions, classes, or modules.

### Client

[clone_client.client.Client](./clone_client/client.py)

> `__init__(self, server, controller_service, state_service)`

All arguments are optional however to make client connect to the remote hand you need to provide `server` argument which is the unique name of the hand provided to you.

**server** `str` - unique name of the hand.
**controller_service** `clone_client.config.CommunicationService` - configuration of controller service. Should be left as default in most cases.
**state_service** `clone_client.config.CommunicationService` - configuration of the state service. Should be left as default in most cases.

> _`property`_ `muscle_order(self)`

Returns a `dict` with indexes as keys and their corresponding muscle names as values.

> _`property`_ `number_of_muscles(self)`

Returns the number (`int`) of muscles connected to the hand.

> `muscle_idx(self, name)`

Returns the index (`int`) of the muscle with given name (`str`).

> `muscle_name(self, idx)`

Returns the name (`str`) of the muscle with given index (`int`).

> `wait_for_desired_pressure(self, timeout)`

Block the execution until timeout (`float`) is reached or until current pressuregen pressure is equal or more than desired pressure.

Raises `clone_client.exceptions.DesiredPressureNotAchievedError` if timeout is reached.

> `set_muscles(self, muscles)`

Sends muscle values in a form of a sequence of floats.

> `get_pressures(self)`

Returns a sequence of floats with current pressure in each muscle.

> `loose_all(self)`

Looses all muscles. Equivalent of sending all `-1` values to `set_muscles` function.

> `lock_all(self)`

Locks all muscles. Equivalent of sending all `0` values to `set_muscles` function.

> `start_pressuregen(self)`

Starts the pressuregen.

> `stop_pressuregen(self)`

Stops the pressuregen.

> `set_pressuregen_pressure(self)`

Sets the desired pressure of the pressuregen. **Currently unimplemented.**

> `get_valve_nodes(self)`

Returns a `set` of `clone_client.types.ValveAddress` with all valve nodes connected to the hand. For higher level programs a `muscle_names` property is recommended.

> `get_pressuregen_info(self)`

Returns a `clone_client.types.pressuregenInfo` with current pressuregen information.

> `get_hand_info(self)`

Returns a `clone_client.types.HandInfo` with current hand information.

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
