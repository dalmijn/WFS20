"""GeoJSON driver."""

from pathlib import Path

from wfs20.driver.base import BaseDriver
from wfs20.struct import Feature


class GeoJSONDriver(BaseDriver):
    """GeoJSON driver."""

    def __init__(
        self,
        file: Path | str,
        buffer_size: int = 52428800,
    ):
        # Supercharge with parent
        BaseDriver.__init__(self, file=file, mode="w", buffer_size=buffer_size)

    def to_file(self):
        """Write to the GeoJSON file."""
        self.ste
        pass

    def write(
        self,
        ft: Feature,
    ):
        """Write a feature to the buffer."""
