from typing import Type, Callable, Union, Optional, Literal, Any

from threading import Thread, RLock
from time import perf_counter, sleep
from functools import partial
from types import TracebackType

import escape
from emptylog import EmptyLogger, LoggerProtocol
from cantok import AbstractToken, SimpleToken, DefaultToken, TimeoutToken
from locklib import ContextLockProtocol

from metronomes.errors import RunStoppedMetronomeError, RunAlreadyStartedMetronomeError, StopNotStartedMetronomeError, StopStoppedMetronomeError


class Metronome:
    def __init__(self, iteration: Union[int, float], callback: Callable[[], Any], suppress_exceptions: bool = True, logger: LoggerProtocol = EmptyLogger(), token: AbstractToken = DefaultToken(), lock_factory: Union[Type[ContextLockProtocol], Callable[[], ContextLockProtocol]] = RLock, sleeping_callback: Callable[[Union[int, float]], Any] = sleep, duration: Optional[Union[int, float]] = None) -> None:
        if iteration <= 0:
            raise ValueError('The duration of the metronome iteration (tick-tock time) must be greater than zero.')

        self.iteration: Union[int, float] = iteration
        self.callback: Callable[[], Any] = callback
        self.suppress_exceptions: bool = suppress_exceptions
        self.logger: LoggerProtocol = logger
        self.token: AbstractToken = SimpleToken(token)
        if duration is not None:
            self.token += self.create_duration_token(duration)
        self.thread: Optional[Thread] = None
        self.started: bool = False
        self.stopped: bool = False
        self.lock: ContextLockProtocol = lock_factory()
        self.sleeping_callback: Callable[[Union[int, float]], Any] = sleeping_callback

    def __enter__(self) -> 'Metronome':
        with self.lock:
            with escape(RunAlreadyStartedMetronomeError):  # type: ignore[operator]
                self.start()
            return self

    def __exit__(self, exception_type: Optional[Type[BaseException]], exception_value: Optional[BaseException], traceback: Optional[TracebackType]) -> Literal[False]:
        with self.lock:
            with escape(StopStoppedMetronomeError):  # type: ignore[operator]
                self.stop()
        return False

    def start(self, token: AbstractToken = DefaultToken(), duration: Optional[Union[int, float]] = None) -> 'Metronome':
        with self.lock:
            if self.stopped:
                raise RunStoppedMetronomeError('Metronomes are disposable, you cannot restart a stopped metronome.')
            if self.started:
                raise RunAlreadyStartedMetronomeError('The metronome has already been launched.')

            if duration is not None:
                token += self.create_duration_token(duration)

            self.thread = Thread(target=self.run_loop, args=(self.token + token,))
            self.thread.daemon = True

            self.logger.info('The metronome starts...')
            self.thread.start()
            self.started = True

        return self

    def stop(self) -> None:
        with self.lock:
            if not self.started:
                raise StopNotStartedMetronomeError("You can't stop a metronome that hasn't been started yet.")
            elif self.stopped:
                raise StopStoppedMetronomeError("You've already stopped this metronome (or it was canceled on its own, for example, when the limit expired), it's impossible to do it twice.")

            self.token.cancel()
            self.thread.join()  # type: ignore[union-attr]

            self.stopped = True
            self.logger.info('The metronome has stopped.')

    def run_loop(self, token: AbstractToken) -> None:
        arguments = [...] if self.suppress_exceptions else []

        if not token:
            self.logger.info('The metronome did not start working because the cancellation token was canceled right at the start.')

        while token:
            start_time = perf_counter()

            self.logger.debug(f'The beginning of the execution of callback "{self.callback.__name__}".')

            with escape(*arguments, logger=self.logger, success_callback=partial(self.logger.debug, f'Callback "{self.callback.__name__}" has been successfully completed.')):  # type: ignore[operator]
                self.callback()

            sleep_time = self.iteration - (perf_counter() - start_time)
            if sleep_time < 0:
                self.logger.warning(f'The callback worked for more than the amount of time allocated for one iteration. The extra time was {sleep_time * -1} seconds.')
            else:
                self.sleeping_callback(sleep_time)

        self.stopped = True

    def create_duration_token(self, duration: Union[int, float]) -> TimeoutToken:
        if duration < 0:
            raise ValueError('The total duration of the metronome operation cannot be less than zero.')
        elif self.iteration > duration:
            raise ValueError('The time of one iteration cannot exceed the running time of the metronome as a whole.')

        return TimeoutToken(duration)
