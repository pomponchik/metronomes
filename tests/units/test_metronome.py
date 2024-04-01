from time import sleep
from threading import active_count

import pytest
import full_match

from metronomes import Metronome


@pytest.mark.parametrize(
    'duration',
    [
        0,
        0.0,
        -0.0,
        -1,
        -1.0,
    ],
)
def test_duration_zero_or_less(duration):
    with pytest.raises(ValueError, match=full_match('The duration of the metronome iteration (tick-tock time) must be greater than zero.')):
        Metronome(duration, lambda: None)


def test_by_default_it_is_creating_a_thread():
    count_before = active_count()

    metronome = Metronome(0.0001, lambda: None)
    assert count_before == active_count()

    metronome.start()
    assert count_before + 1 == active_count()

    metronome.stop()
    assert count_before == active_count()


def test_alternation_of_sleep_and_callback():
    actions = []

    metronome = Metronome(0.0001, lambda: actions.append(1), sleeping_callback=lambda: actions.append(2))
    metronome.start()

    sleep(0.1)

    metronome.stop()

    for index, action in enumerate(actions):
        if index % 2 == 0:
            assert action == 1
        else:
            assert action == 2
