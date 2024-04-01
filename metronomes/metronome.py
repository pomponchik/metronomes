from typing import Type, Callable, Union, Optional, Any
from threading import Thread, Lock
from time import perf_counter, sleep

import escape
from emptylog import EmptyLogger, LoggerProtocol
from cantok import AbstractToken, SimpleToken
from locklib import ContextLockProtocol

from metronomes.errors import RunStoppedMetronomeError, RunAlreadyStartedMetronomeError, StopNotStartedMetronomeError, StopStoppedMetronomeError


class Metronome:
    def __init__(self, duration: Union[int, float], callback: Callable[[], Any], suppress_exceptions: bool = True, logger: LoggerProtocol = EmptyLogger(), cancellation_token: Optional[AbstractToken] = None, lock_factory: Union[Type[ContextLockProtocol], Callable[[], ContextLockProtocol]] = Lock, sleeping_callback: Callable[[Union[int, float]], Any] = sleep) -> None:
        if duration <= 0:
            raise ValueError('The duration of the metronome iteration (tick-tock time) must be greater than zero.')

        self.duration: Union[int, float] = duration
        self.callback: Callable[[], Any] = callback
        self.suppress_exceptions: bool = suppress_exceptions
        self.logger: LoggerProtocol = logger
        self.token: AbstractToken = SimpleToken(cancellation_token) if cancellation_token is not None else SimpleToken()
        self.thread: Optional[Thread] = None
        self.started: bool = False
        self.stopped: bool = False
        self.lock: ContextLockProtocol = lock_factory()
        self.sleeping_callback: Callable[[Union[int, float]], Any] = sleeping_callback

    def start(self) -> 'Metronome':
        with self.lock:
            if self.stopped:
                raise RunStoppedMetronomeError('Metronomes are disposable, you cannot restart a stopped metronome.')
            if self.started:
                raise RunAlreadyStartedMetronomeError('The metronome has already been launched.')

            self.thread = Thread(target=self.run_loop, args=())
            self.thread.daemon = True
            self.thread.start()

            self.started = True
            self.logger.info('The metronome has started.')

    def stop(self) -> None:
        with self.lock:
            if not self.started:
                raise StopNotStartedMetronomeError("You can't stop a metronome that hasn't been started yet.")
            elif self.stopped:
                raise StopStoppedMetronomeError("You've already stopped this metronome, it's impossible to do it twice.")

            self.token.cancel()
            self.thread.join()  # type: ignore[union-attr]

            self.stopped = True
            self.logger.info('The metronome has stopped.')

    def run_loop(self) -> None:
        arguments = [...] if self.suppress_exceptions else []

        while self.token:
            start_time = perf_counter()

            with escape(*arguments, logger=self.logger):  # type: ignore[operator]
                self.callback()

            sleep_time = self.duration - (perf_counter() - start_time)
            if sleep_time < 0:
                self.logger.warning(f'The callback worked for more than the amount of time allocated for one iteration. The extra time was {sleep_time * -1} seconds.')
            else:
                self.sleeping_callback(sleep_time)

        if not token:
            with escape(...):
                self.stop()
