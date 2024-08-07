from time import sleep
from copy import copy
from threading import active_count

import pytest
import full_match
from emptylog import MemoryLogger
from cantok import SimpleToken

from metronomes import Metronome
from metronomes.errors import RunStoppedMetronomeError, RunAlreadyStartedMetronomeError, StopNotStartedMetronomeError, StopStoppedMetronomeError


@pytest.mark.parametrize(
    'iteration',
    [
        0,
        0.0,
        -0.0,
        -1,
        -1.0,
    ],
)
def test_iteration_time_zero_or_less(iteration):
    with pytest.raises(ValueError, match=full_match('The duration of the metronome iteration (tick-tock time) must be greater than zero.')):
        Metronome(iteration, lambda: None)


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

    with pytest.raises(StopStoppedMetronomeError, match=full_match("You've already stopped this metronome (or it was canceled on its own, for example, when the limit expired), it's impossible to do it twice.")):
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
    assert logger.data.info[0].message == 'The metronome starts...'

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


def test_cancellation_token_is_stopping_the_metronome():
    sleep_time = 0.0001
    def callback(): pass
    logger = MemoryLogger()
    token = SimpleToken()
    metronome = Metronome(sleep_time, callback, logger=logger, token=token)

    count_before = active_count()
    metronome.start()

    assert active_count() == count_before + 1
    assert metronome.stopped == False

    token.cancel()
    sleep(sleep_time * 200)

    assert active_count() == count_before
    assert metronome.stopped == True


def test_cancellation_token_is_stopping_the_metronome_in_start_method():
    sleep_time = 0.0001
    def callback(): pass
    logger = MemoryLogger()
    token = SimpleToken()
    metronome = Metronome(sleep_time, callback, logger=logger)

    count_before = active_count()
    metronome.start(token=token)

    assert active_count() == count_before + 1
    assert metronome.stopped == False

    token.cancel()
    sleep(sleep_time * 200)

    assert active_count() == count_before
    assert metronome.stopped == True


@pytest.mark.parametrize(
    ['first_token', 'second_token'],
    [
        (SimpleToken(), SimpleToken(cancelled=True)),
        (SimpleToken(cancelled=True), SimpleToken()),
        (SimpleToken(cancelled=True), SimpleToken(cancelled=True)),
    ],
)
def test_start_with_cancelled_token(first_token, second_token):
    actions = []
    logger = MemoryLogger()
    metronome = Metronome(0.0001, lambda: actions.append(True), token=first_token, logger=logger)

    metronome.start(token=second_token)
    sleep(0.0001)

    assert metronome.stopped
    assert not actions
    assert len(logger.data) == 2
    assert len(logger.data.info) == 2
    assert logger.data.info[0].message == 'The metronome starts...'
    assert logger.data.info[1].message == 'The metronome did not start working because the cancellation token was canceled right at the start.'


def test_behavior_when_the_callback_time_is_bigger_than_loop_time():
    actions = []
    loop_time = 0.0001
    sleep_time = loop_time * 5
    def callback(): (sleep(sleep_time), actions.append(1))
    logger = MemoryLogger()
    token = SimpleToken()
    metronome = Metronome(loop_time, callback, logger=logger, token=token, sleeping_callback=lambda x: actions.append(2))

    metronome.start()

    sleep(sleep_time * 10)

    metronome.stop()

    assert len(actions)
    assert all(x == 1 for x in actions)

    assert len(logger.data.warning)

    for log_item in logger.data.warning:
        assert log_item.message.startswith('The callback worked for more than the amount of time allocated for one iteration. The extra time was ')
        assert log_item.message.endswith(' seconds.')


def test_exceptions_escaping():
    sleep_time = 0.0001
    def callback(): raise ValueError('kek')
    logger = MemoryLogger()
    metronome = Metronome(sleep_time, callback, logger=logger)

    metronome.start()

    sleep(sleep_time * 10)

    metronome.stop()

    assert len(logger.data.exception) > 0


def test_iteration_more_than_duration():
    with pytest.raises(ValueError, match=full_match('The time of one iteration cannot exceed the running time of the metronome as a whole.')):
        Metronome(5, lambda: None, duration=1)


def test_iteration_more_than_duration_in_start_method():
    with pytest.raises(ValueError, match=full_match('The time of one iteration cannot exceed the running time of the metronome as a whole.')):
        Metronome(5, lambda: None).start(duration=1)


def test_duration_less_than_zero():
    with pytest.raises(ValueError, match=full_match('The total duration of the metronome operation cannot be less than zero.')):
        Metronome(0.5, lambda: None, duration=-1)


def test_duration_less_than_zero_in_start_method():
    with pytest.raises(ValueError, match=full_match('The total duration of the metronome operation cannot be less than zero.')):
        Metronome(0.5, lambda: None).start(duration=-1)


def test_set_duration_time():
    metronome = Metronome(0.00001, lambda: None, duration=0.001)

    assert not metronome.stopped

    metronome.start()
    sleep(0.1)

    assert metronome.stopped


def test_set_duration_in_start_method():
    metronome = Metronome(0.00001, lambda: None)

    assert not metronome.stopped

    metronome.start(duration=0.001)
    sleep(0.1)

    assert metronome.stopped


def test_context_manager_basics():
    actions = []
    metronome = Metronome(0.00001, lambda: actions.append(1))

    assert not metronome.stopped

    with metronome:
        sleep(0.1)

    assert actions
    assert metronome.stopped


def test_context_manager_with_started_metronome():
    actions = []
    metronome = Metronome(0.00001, lambda: actions.append(1)).start()

    assert not metronome.stopped
    assert metronome.started

    with metronome:
        sleep(0.1)

    assert actions
    assert metronome.stopped


def test_stop_metronome_into_context_manager():
    actions = []
    metronome = Metronome(0.00001, lambda: actions.append(1))

    assert not metronome.stopped

    with metronome:
        sleep(0.1)
        metronome.stop()

    assert actions
    assert metronome.stopped


def test_raise_into_context_manager():
    metronome = Metronome(0.00001, lambda: None)

    with pytest.raises(ValueError, match=full_match('text')):
        with metronome:
            raise ValueError('text')


def test_numbers_of_threads_into_context_manager():
    count_before = active_count()
    metronome = Metronome(0.00001, lambda: None)

    assert count_before == active_count()

    with metronome:
        assert count_before + 1 == active_count()

    assert count_before == active_count()
