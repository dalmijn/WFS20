"""Template for drivers."""

from abc import ABCMeta, abstractmethod
from io import BytesIO, FileIO
from pathlib import Path

from wfs20.struct import Feature


class BaseDriver(metaclass=ABCMeta):
    """Base class for geometry drivers."""

    def __init__(
        self,
        file: Path | str,
        mode="wb",
        buffer_size: int = 52428800,  # 50 mb
    ):
        # Some driver variables
        self._closed = False
        self.srs = None

        # Setup the internal buffer and the stream to the file
        self.buffer = BytesIO()
        self.stream = FileIO(file=file, mode=mode)
        self.buffer_size = buffer_size

        # Write the header of the file.
        self.write(self.header)

    @property
    def closed(self):
        """Return whether the driver has been shut down."""
        return self._closed

    @abstractmethod
    @property
    def header(self):
        """Return the header of the driver."""
        ...

    def close(self):
        """Close the driver."""
        self.flush()
        self.stream.close()
        self.buffer.close()
        self.stream = None
        self.buffer = None
        self._closed = True

    def flush(self):
        """Flush everything to the file."""
        self.to_file()
        self.stream.flush()

    @abstractmethod
    def to_file(self):
        """Write the buffer to the file."""
        ...

    @abstractmethod
    def write(
        self,
        ft: Feature,
    ):
        """Write to the internal buffer."""
        ...
