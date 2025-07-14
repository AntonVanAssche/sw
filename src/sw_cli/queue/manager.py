#!/usr/bin/env python

import random
from pathlib import Path

from sw_cli.queue.errors import QueueError, QueueNotFoundError, QueueReadError, QueueWriteError


class QueueManager:
    def __init__(self, queue_file: Path):
        self.queue_file = queue_file
        self._ensure_file()

    def _ensure_file(self):
        try:
            if not self.queue_file.exists():
                self.queue_file.parent.mkdir(parents=True, exist_ok=True)
                self.queue_file.write_text("", encoding="utf-8")
        except Exception as e:
            raise QueueWriteError(f"Failed to create queue file: {e}") from e

    def get(self) -> list[str]:
        try:
            with open(self.queue_file, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError as e:
            raise QueueNotFoundError(f"Queue file not found: {self.queue_file}") from e
        except Exception as e:
            raise QueueReadError(f"Failed to read queue file: {e}") from e

    def add(self, paths: list[str]) -> None:
        try:
            current_queue = self.get()
            new_queue = current_queue + [path for path in paths if path not in current_queue]
            self._write(new_queue)
        except (QueueReadError, QueueWriteError) as e:
            raise e
        except Exception as e:
            raise QueueError(f"An unexpected error occurred while adding items: {e}") from e

    def remove(self, paths: list[str]) -> None:
        try:
            current_queue = self.get()
            new_queue = [item for item in current_queue if item not in paths]
            self._write(new_queue)
        except (QueueReadError, QueueWriteError) as e:
            raise e
        except Exception as e:
            raise QueueError(f"An unexpected error occurred while removing items: {e}") from e

    def clear(self) -> None:
        try:
            self._write([])
        except QueueWriteError as e:
            raise e
        except Exception as e:
            raise QueueError(f"An unexpected error occurred while clearing the queue: {e}") from e

    def shuffle(self) -> None:
        try:
            current_queue = self.get()
            random.shuffle(current_queue)
            self._write(current_queue)
        except (QueueReadError, QueueWriteError) as e:
            raise e
        except Exception as e:
            raise QueueError(f"An unexpected error occurred while shuffling the queue: {e}") from e

    def _write(self, queue: list[str]) -> None:
        try:
            with open(self.queue_file, "w", encoding="utf-8") as f:
                for item in queue:
                    f.write(f"{item}\n")
        except Exception as e:
            raise QueueWriteError(f"Failed to write queue file: {e}") from e
