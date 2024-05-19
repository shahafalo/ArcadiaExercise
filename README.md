# Arm Control Python Script

This script controls the movement of an arm using a motor, encoder, and microswitch. It allows the arm to move in specified directions for given distances while ensuring safety and accuracy through various checks and validations.

## Usage

To use this script, create an instance of the `Arm` class with the required motor, encoder, and microswitch objects, and then call the `move_arm` method with the desired direction and distance.

### Example

```
import asyncio
from interface_stubs import Encoder, MicroSwitch, Motor
from arm_controller import Arm

# Initialize motor, encoder, and microswitch objects
motor = Motor()
encoder = Encoder()
microswitch = MicroSwitch()

# Create Arm instance
arm = Arm(motor, encoder, microswitch)

# Move arm asynchronously
async def main():
    await arm.move_arm(direction=1, distance=10)

asyncio.run(main())
