import pytest
from unittest.mock import MagicMock, patch
from arm_controller import Arm
from exceptions import InvalidDistanceError, InvalidDirectionError


@pytest.fixture
def motor():
    return MagicMock()

@pytest.fixture
def encoder():
    return MagicMock()

@pytest.fixture
def microswitch():
    return MagicMock()

@pytest.fixture
def arm(motor, encoder, microswitch):
    return Arm(motor, encoder, microswitch)

@pytest.fixture
def mock_logging():
    with patch('arm_controller.logging') as mock_logging:
        yield mock_logging

@pytest.mark.asyncio
async def test_move_arm_reaches_target_distance(arm, motor, encoder, microswitch, mock_logging):
    # Set up the mocks
    encoder.status.side_effect = [0, 0, 1, 1] * 20  # Include 2 checks per toggle
    microswitch.status.return_value = 0

    await arm.move_arm(1, 5)  # Move arm left for 5 units

    assert motor.on.call_count == 1
    assert motor.off.call_count == 1
    assert encoder.status.call_count == 41  # (units * 20 degrees / 5 degrees per flip) * 2 checks per flip + 1 initial status
    mock_logging.error.assert_not_called()  # No error should be logged


@pytest.mark.asyncio
async def test_move_arm_stops_on_microswitch_activation(arm, motor, encoder, microswitch, mock_logging):
    # Set up the mocks
    encoder.status.side_effect = [0, 0, 1, 1] * 10
    microswitch.status.side_effect = [0, 0, 1]  # Activate microswitch after some time

    await arm.move_arm(1, 5)  # Move arm left for 5 units

    assert motor.on.call_count == 1
    assert motor.off.call_count == 1
    assert encoder.status.call_count == 3  # Stopped early due to microswitch
    assert mock_logging.info.call_args_list[0][0][0] == "Stop: MicroSwitch activated."
    assert mock_logging.info.call_args_list[1][0][0] == "Finished moving, Moved 0 units"


@pytest.mark.asyncio
async def test_invalid_direction(arm, motor, mock_logging):
    with pytest.raises(InvalidDirectionError):
        await arm.move_arm(3, 5)  # Invalid direction
    assert motor.on.call_count == 0
    assert motor.off.call_count == 0
    mock_logging.error.assert_called_with("Invalid direction: 3, Valid directions are: left (1) or right (2)")


@pytest.mark.asyncio
async def test_invalid_distance(arm, motor, mock_logging):
    with pytest.raises(InvalidDistanceError):
        await arm.move_arm(1, 0)  # Invalid distance
    assert motor.on.call_count == 0
    assert motor.off.call_count == 0
    mock_logging.error.assert_called_with("Invalid distance: 0, should be a natural positive number")
