from time import sleep
from metronomes import Metronome


def test_quick_start():
    actions = []
    metronome = Metronome(0.02, lambda: actions.append(1))

    metronome.start()
    sleep(0.1)
    metronome.stop()

    assert len(actions) > 0
    assert all(x == 1 for x in actions)
