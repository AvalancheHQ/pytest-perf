from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dist_instrument_hooks import lib as LibType

SUPPORTS_PERF_TRAMPOLINE = sys.version_info >= (3, 12)


class InstrumentHooks:
    """Zig library wrapper class providing benchmark measurement functionality."""

    lib: LibType | None
    instance: int | None

    def __init__(self) -> None:
        self.codspeed_env = os.environ.get("CODSPEED_ENV") is not None
        if self.codspeed_env and SUPPORTS_PERF_TRAMPOLINE:
            sys.activate_stack_trampoline("perf")  # type: ignore

        try:
            from .dist_instrument_hooks import lib  # type: ignore

            instance = lib.instrument_hooks_init()
            if instance == 0:
                raise RuntimeError("Failed to initialize instrumentation library")

            self.instance = instance
            self.lib = lib
        except Exception:
            self.lib = None
            self.instance = None

    def __del__(self):
        if self.lib is None:
            return

        self.lib.instrument_hooks_deinit(self.instance)

    def is_codspeed_env(self) -> bool:
        """Check if the current environment is a CodSpeed environment."""
        return self.codspeed_env

    def start_benchmark(self) -> None:
        """Start a new benchmark measurement."""
        if self.lib is None:
            return

        self.lib.instrument_hooks_start_benchmark(self.instance)

    def stop_benchmark(self) -> None:
        """Stop the current benchmark measurement."""
        if self.lib is None:
            return

        self.lib.instrument_hooks_stop_benchmark(self.instance)

    def set_current_benchmark(self, uri: str, pid: int | None = None) -> None:
        """Set the current benchmark URI and process ID.

        Args:
            uri: The benchmark URI string identifier
            pid: Optional process ID (defaults to current process)
        """
        if self.lib is None:
            return

        if pid is None:
            pid = os.getpid()
        self.lib.instrument_hooks_current_benchmark(
            self.instance, pid, uri.encode("ascii")
        )

    def set_integration(self, name: str, version: str) -> None:
        """Set the integration name and version."""
        if self.lib is None:
            return

        self.lib.instrument_hooks_set_integration(
            self.instance, name.encode("ascii"), version.encode("ascii")
        )

    def is_instrumented(self) -> bool:
        """Check if instrumentation is active."""
        if self.lib is None:
            return False

        return self.lib.instrument_hooks_is_instrumented(self.instance)
