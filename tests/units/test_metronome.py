from time import sleep
from copy import copy
from threading import active_count

import pytest
import full_match
from emptylog import MemoryLogger

from metronomes import Metronome
from metronomes.errors import RunStoppedMetronomeError, RunAlreadyStartedMetronomeError, StopNotStartedMetronomeError, StopStoppedMetronomeError


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

    metronome = Metronome(0.1, lambda: (actions.append(1), sleep(0.0001)), sleeping_callback=lambda x: actions.append(2))
    metronome.start()

    sleep(0.1)

    metronome.stop()

    assert actions

    for index, action in enumerate(actions):
        if index % 2 == 0:
            assert action == 1
        else:
            assert action == 2


def test_start_started():
    metronome = Metronome(0.0001, lambda: None)

    metronome.start()

    with pytest.raises(RunAlreadyStartedMetronomeError, match=full_match('The metronome has already been launched.')):
        metronome.start()

    metronome.stop()


def test_stop_stopped():
    metronome = Metronome(0.0001, lambda: None)

    metronome.start()
    metronome.stop()

    with pytest.raises(StopStoppedMetronomeError, match=full_match("You've already stopped this metronome, it's impossible to do it twice.")):
        metronome.stop()


def test_start_stopped():
    metronome = Metronome(0.0001, lambda: None)

    metronome.start()
    metronome.stop()

    with pytest.raises(RunStoppedMetronomeError, match=full_match('Metronomes are disposable, you cannot restart a stopped metronome.')):
        metronome.start()


def test_stop_not_started():
    metronome = Metronome(0.0001, lambda: None)

    with pytest.raises(StopNotStartedMetronomeError, match=full_match("You can't stop a metronome that hasn't been started yet.")):
        metronome.stop()


def test_start_returns_the_same_metronome():
    metronome = Metronome(0.0001, lambda: None)

    assert metronome.start() is metronome

    metronome.stop()


def test_normal_logs_order():
    def callback(): pass
    logger = MemoryLogger()
    metronome = Metronome(0.0001, callback, logger=logger)

    assert len(logger.data) == 0

    metronome.start()

    assert len(logger.data.info) == 1
    assert logger.data.info[0].message == 'The metronome has started.'

    sleep(0.0001 * 10)

    assert len(logger.data) >= 3
    assert len(logger.data.debug) >= 2

    for index, log_item in enumerate(copy(logger.data.debug)):
        if index % 2 == 0:
            assert log_item.message == 'The beginning of the execution of callback "callback".'
        else:
            assert log_item.message == 'Callback "callback" has been successfully completed.'

    metronome.stop()

    assert len(logger.data.info) == 2
    assert logger.data.info[1].message == 'The metronome has stopped.'
