import os
import pathlib

from typing import Optional

from jellyfin_webhooks.utils.constants import constants as c
from jellyfin_webhooks.utils.functions import markup_language_to_json

class Series:
    def __init__(
        self,
        name: str,
        base_dir: str,
        non_video_file_formats: list[str] = c.NON_VIDEO_FILE_FORMATS
    ):
        self.name = name
        self.directory = pathlib.Path(base_dir)
        self.seasons: dict[int, 'Season'] = {}
        self.non_video_file_formats = [f.lower().replace('.', '') for f in non_video_file_formats]

    def __getitem__(self, key: int):
        return self.get(key)

    @property
    def metadata(self):
        if self._metadata:
            return self._metadata

        self._metadata = {}
        for file in self.directory.iterdir():
            if file.suffix.lower() in ('.nfo', '.xml'):
                self._metadata.update(markup_language_to_json(self.directory / file))
        return self._metadata

    def get(self, season_num: int) -> 'Season':
        '''
            Tries to fetch the season associated with `season_num`
        '''
        if self.seasons.get(season_num):
            return self.seasons[season_num]
        
        for folder in self.directory.iterdir():
            if not folder.name.startswith('Season '):
                continue
            folder_season = int(folder.name.split(' ')[-1])
            if folder_season != season_num:
                continue
            season = Season(
                self,
                folder_season
            )
            self.add_season(season)

        if season_num == -1:
            return self.seasons[max(self.seasons.keys())]
        return self.seasons[season_num]

    def add_season(self, season: 'Season'):
        if season.season_num in self.seasons.keys():
            return False
        self.seasons[season.season_num] = season
        return True

    def replace_season(self, season: 'Season'):
        if season.season_num not in self.seasons.keys():
            return False
        self.seasons[season.season_num] = season
        return True

    def refresh(self, refresh_episodes: bool=True):
        '''
        Refreshes season list for `self` serie
        
        '''
        for folder in self.directory.iterdir():
            if not folder.name.startswith('Season '):
                continue

            season = Season(
                self,
                int(folder.name.split(' ')[-1])
            )
            if refresh_episodes:
                season.refresh()
            self.add_season(season)
        return True


class Season:

    def __init__(
        self,
        series: Series,
        season_num: int,
    ):
        self.episodes: dict[int, 'Episode'] = {}
        self.series = series
        self.season_num = season_num
        self.directory = series.directory / f'Season {self.season_num}'

    def __getitem__(self, key: int):
        return self.get(key)


    def get(self, episode_num: int) -> 'Episode':
        '''
            Tries to fetch the episode associated with `episode_num`
        '''
        if self.episodes.get(episode_num):
            return self.episodes[episode_num]
        
        self.refresh(stop_on=episode_num)

        if episode_num == -1:
            return self.episodes[max(self.episodes.keys())]
        return self.episodes[episode_num]

    def add_episode(self, episode: 'Episode'):
        if episode.episode_num in self.episodes.keys():
            return False

        self.episodes[episode.episode_num] = episode
        return True

    def replace_episode(self, episode: 'Episode'):
        if episode.episode_num not in self.episodes.keys():
            return False
        self.episodes[episode.episode_num] = episode
        return True

    def refresh(self, stop_on: int=0):
        '''
        Refreshes episode list for `self` season.
        Stops at `stop_on` episode num
        
        :param self: Description
        '''
        episode_list = {}
        for file in self.directory.iterdir():
            filename_preffix = file.name.replace(file.suffix, '')
            
            # Ignore `thumbnails`
            if filename_preffix.lower().endswith('-thumb'):
                continue

            if filename_preffix.lower().strip('-thumb') in episode_list:
                continue
            episode = Episode(
                season = self,
                episode_num=None,
                name=None,
                filename_preffix=filename_preffix,
            )
            episode_list[filename_preffix.lower()] = episode
            self.add_episode(episode)

            if stop_on == episode.episode_num:
                return True
        return True
        

class Episode:

    def __init__(
        self,
        season: Season,
        episode_num: Optional[int]=None,
        name: Optional[str]=None,
        filename_preffix: Optional[str]=None,
    ) -> None:
        '''
        Either `episode_num` and `name` exist, or `filename_preffix` must exist
        
        :param self: Description
        :param season: Description
        :type season: Season
        :param episode_num: Description
        :type episode_num: Optional[int]
        :param name: Description
        :type name: Optional[str]
        :param filename_preffix: Description
        :type filename_preffix: Optional[str]
        :param non_video_file_formats: Description
        :type non_video_file_formats: list[str]
        '''
        assert filename_preffix is not None or (episode_num is not None and name is not None), 'Can not create an episode without details of the episode\n Please provide either `episode_num` and `name`, or `filename_preffix`'
        self._metadata = None
        self._file = None
        self._filename_preffix = None
        self._name = None
        self._episode_num = None

        if filename_preffix:
            self._filename_preffix = filename_preffix
        if episode_num:
            self._name = name
            self._episode_num = episode_num
        
        self.season = season

    @property
    def filename_preffix(self) -> str:
        if self._filename_preffix:
            return self._filename_preffix

        for file in self.season.directory.iterdir():
            if not file.suffix.lower() in ('.nfo', '.xml'):
                continue

            # Read Metadata and confirm if it's correspondent to `self` or not
            metadata = markup_language_to_json(self.season.directory / file)
            if int(metadata['episodedetails']['season']) != self.season.season_num:
                continue
            
            if int(metadata['episodedetails']['episode']) != self.episode_num:
                continue

            self._filename_preffix = file.name.replace(file.suffix, '')
            break
        
        assert self._filename_preffix is not None, f'Could not find data corresponding to Episode {self}'
        return self._filename_preffix
    
    @property
    def metadata(self):
        if self._metadata:
            return self._metadata

        # Update metadata with both `.xml` and `.nfo`
        self._metadata = {}
        for suffix in ('xml', 'nfo'):
            self._metadata.update(
                markup_language_to_json(self.season.directory / f'{self.filename_preffix}.{suffix}')
            )
        assert self._metadata != {}, f'Could not find metadata related to episode `{self}`'
        return self._metadata

    @property
    def file(self) -> pathlib.Path:
        if self._file:
            return self._file

        for file in self.season.directory.iterdir():
            if not file.name.lower().startswith(self.filename_preffix.lower()):
                continue

            # Find file that's in VIDEO format
            if file.suffix.lower().replace('.', '') not in self.season.series.non_video_file_formats:
                self._file = file
                break

        assert self._file is not None, f'Could not find file corresponding to Episode {self}'
        return self._file

    @property
    def episode_num(self) -> int:
        if self._episode_num is not None:
            return self._episode_num
        
        self._episode_num = int(self.metadata['episodedetails']['episode'])
        return self._episode_num
        
    @property
    def name(self) -> str:
        if self._name is not None:
            return self._name
        
        self._name = self.metadata['episodedetails']['title']
        return self._name

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


