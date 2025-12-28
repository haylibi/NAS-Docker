import os
import pathlib

from jellyfin_webhooks.utils.constants import constants as c
from jellyfin_webhooks.utils.functions import markup_language_to_json


class Movie:
    def __init__(
        self,
        name: str,
        base_dir: str,
        non_video_file_formats: list[str] = c.NON_VIDEO_FILE_FORMATS
    ):
        self.directory = pathlib.Path(base_dir)
        self.non_video_file_formats = [f.lower().replace('.', '') for f in non_video_file_formats]

        self.name = name
        self._metadata = None
        self._file = None


    @property
    def file(self) -> pathlib.Path:
        if self._file:
            return self._file

        for file in self.directory.iterdir():
            # Find file that's in VIDEO format
            if file.suffix.lower().replace('.', '') not in self.non_video_file_formats:
                self._file = file
                break

        assert self._file is not None, f'Could not find file corresponding to Episode {self}'
        return self._file


    def get_torrent_path(self):
        assert isinstance(c.TORRENTS_DATA_ROOT, str), 'Couldnt get `DATA_ROOT` from environment'
        assert os.path.exists(c.TORRENTS_DATA_ROOT), 'DATA_ROOT path does not exist'

        for root, _, files in os.walk(c.TORRENTS_DATA_ROOT):
            for filename in files:
                full_path = pathlib.Path(root) / filename
                
                # Found a match
                if os.path.samefile(full_path, self.file):
                    return full_path
        return None


