from time import sleep
from metronomes import Metronome



def test_quick_start():
    actions = []
    metronome = Metronome(0.2, lambda: actions.append(1))

    metronome.start()
    sleep(1)
    metronome.stop()

    assert len(actions) == 5
