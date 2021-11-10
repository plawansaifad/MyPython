import nba_constants as constants

from datetime import datetime, timedelta
import os

from requests import get
from nba_constants import League

HAS_PANDAS = True
try:
    from pandas import DataFrame
except ImportError:
    HAS_PANDAS = False

HAS_REQUESTS_CACHE = True
CACHE_EXPIRE_MINUTES = int(os.getenv('NBA_PY_CACHE_EXPIRE_MINUTES', 10))
try:
    from requests_cache import install_cache
    install_cache(cache_name='nba_cache',
                  expire_after=timedelta(minutes=CACHE_EXPIRE_MINUTES))
except ImportError:
    HAS_REQUESTS_CACHE = False

# Constants
TODAY = datetime.today()
BASE_URL = 'http://stats.nba.com/stats/{endpoint}'
HEADERS = {'Host': 'stats.nba.com',
            'Accept': 'application/json, text/plain, */*',
            'x-nba-stats-token': 'true',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36',
            'x-nba-stats-origin': 'stats',
            'Origin': 'https://www.nba.com',
            'Referer': 'https://www.nba.com/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9}'
           }

def _api_scrape(json_inp, ndx):
    """
    Internal method to streamline the getting of data from the json
    Args:
        json_inp (json): json input from our caller
        ndx (int): index where the data is located in the api
    Returns:
        If pandas is present:
            DataFrame (pandas.DataFrame): data set from ndx within the
            API's json
        else:
            A dictionary of both headers and values from the page
    """

    try:
        headers = json_inp['resultSets'][ndx]['headers']
        values = json_inp['resultSets'][ndx]['rowSet']
    except KeyError:
        # This is so ugly but this is what you get when your data comes out
        # in not a standard format
        try:
            headers = json_inp['resultSet'][ndx]['headers']
            values = json_inp['resultSet'][ndx]['rowSet']
        except KeyError:
            # Added for results that only include one set (ex. LeagueLeaders)
            headers = json_inp['resultSet']['headers']
            values = json_inp['resultSet']['rowSet']
    if HAS_PANDAS:
        return DataFrame(values, columns=headers)
    else:
        # Taken from www.github.com/bradleyfay/py-goldsberry
        return [dict(zip(headers, value)) for value in values]


def _get_json(endpoint, params, referer='scores'):
    """
    Internal method to streamline our requests / json getting
    Args:
        endpoint (str): endpoint to be called from the API
        params (dict): parameters to be passed to the API
    Raises:
        HTTPError: if requests hits a status code != 200
    Returns:
        json (json): json object for selected API call
    """
    h = dict(HEADERS)
   # h['referer'] = 'http://stats.nba.com/{ref}/'.format(ref=referer)
    _get = get(BASE_URL.format(endpoint=endpoint), params=params,
               headers=h)
     #print _get.url
    print(BASE_URL.format(endpoint=endpoint))
    _get.raise_for_status()
    return _get.json()

class PlayerNotFoundException(Exception):
    pass

def get_player(first_name,
               last_name=None,
               season=constants.CURRENT_SEASON,
               only_current=0,
               just_id=True):
    """
    Calls our PlayerList class to get a full list of players and then returns
    just an id if specified or the full row of player information
    Args:
        :first_name: First name of the player
        :last_name: Last name of the player
        (this is None if the player only has first name [Nene])
        :only_current: Only wants the current list of players
        :just_id: Only wants the id of the player
    Returns:
        Either the ID or full row of information of the player inputted
    Raises:
        :PlayerNotFoundException::
    """
    if last_name is None:
        name = first_name.lower()
    else:
        name = '{}, {}'.format(last_name, first_name).lower()
    pl = PlayerList(season=season, only_current=only_current).info()
    hdr = 'DISPLAY_LAST_COMMA_FIRST'
    if HAS_PANDAS:
        item = pl[pl.DISPLAY_LAST_COMMA_FIRST.str.lower() == name]
    else:
        item = next(plyr for plyr in pl if str(plyr[hdr]).lower() == name)
    if len(item) == 0:
        raise PlayerNotFoundException
    elif just_id:
        return item['PERSON_ID']
    else:
        return item

class PlayerList:
    """
    Contains a list of all players for a season, if specified, and will only
    contain current players if specified as well
    Args:
        :league_id: ID for the league to look in (Default is 00)
        :season: Season given to look up
        :only_current: Restrict lookup to only current players
    Attributes:
        :json: Contains the full json dump to play around with
    """
    _endpoint = 'commonallplayers'

    def __init__(self,
                 league_id=constants.League.NBA,
                 season=constants.CURRENT_SEASON,
                 only_current=1):
        self.json = _get_json(endpoint=self._endpoint,
                              params={'LeagueID': league_id,
                                      'Season': season,
                                      'IsOnlyCurrentSeason': only_current})

    def info(self):
        return _api_scrape(self.json, 0)

class PlayerStats:
    _endpoint = 'leaguedashplayerstats'

    def __init__(self,
                 season_type=constants.SeasonType.Default,
                 measure_type=constants.MeasureType.Default,
                 per_mode=constants.PerMode.Default,
                 plus_minus=constants.PlusMinus.Default,
                 pace_adjust=constants.PaceAdjust.Default,
                 rank=constants.Rank.Default,
                 season=constants.CURRENT_SEASON,
                 playoff_round=constants.PlayoffRound.Default,
                 outcome=constants.Outcome.Default,
                 location=constants.Location.Default,
                 month=constants.Month.Default,
                 season_segment=constants.SeasonSegment.Default,
                 date_from=constants.DateFrom.Default,
                 date_to=constants.DateTo.Default,
                 opponent_team_id=constants.OpponentTeamID.Default,
                 vs_conference=constants.VsConference.Default,
                 vs_division=constants.VsDivision.Default,
                 team_id=constants.TeamID.Default,
                 conference=constants.Conference.Default,
                 division=constants.Division.Default,
                 game_segment=constants.GameSegment.Default,
                 period=constants.Period.Default,
                 shot_clock_range=constants.ShotClockRange.Default,
                 last_n_games=constants.LastNGames.Default,
                 game_scope=constants.Game_Scope.Default,
                 player_experience=constants.PlayerExperience.Default,
                 player_position=constants.PlayerPosition.Default,
                 starter_bench=constants.StarterBench.Default,
                 draft_year=constants.DraftYear.Default,
                 draft_pick=constants.DraftPick.Default,
                 college=constants.College.Default,
                 country=constants.Country.Default,
                 height=constants.Height.Default,
                 weight=constants.Weight.Default
                 ):
        self.json = _get_json(endpoint=self._endpoint,
                              params={'SeasonType': season_type,
                                      'MeasureType': measure_type,
                                      'PerMode': per_mode,
                                      'PlusMinus': plus_minus,
                                      'PaceAdjust': pace_adjust,
                                      'Rank': rank,
                                      'Season': season,
                                      'PORound': playoff_round,
                                      'Outcome': outcome,
                                      'Location': location,
                                      'Month': month,
                                      'SeasonSegment': season_segment,
                                      'DateFrom': date_from,
                                      'DateTo': date_to,
                                      'OpponentTeamID': opponent_team_id,
                                      'VsConference': vs_conference,
                                      'VsDivision': vs_division,
                                      'TeamID': team_id,
                                      'Conference': conference,
                                      'Division': division,
                                      'GameSegment': game_segment,
                                      'Period': period,
                                      'ShotClockRange': shot_clock_range,
                                      'LastNGames': last_n_games,
                                      'GameScope': game_scope,
                                      'PlayerExperience': player_experience,
                                      'PlayerPosition': player_position,
                                      'StarterBench': starter_bench,
                                      'DraftYear': draft_year,
                                      'DraftPick': draft_pick,
                                      'College': college,
                                      'Country': country,
                                      'Height': height,
                                      'Weight': weight
                                      })

    def overall(self):
        return _api_scrape(self.json, 0)

class ShotChart:
    _endpoint = 'shotchartdetail'

    def __init__(self,
                 player_id,
                 team_id=constants.TeamID.Default,
                 game_id=constants.GameID.Default,
                 league_id=constants.League.Default,
                 season=constants.CURRENT_SEASON,
                 season_type=constants.SeasonType.Default,
                 outcome=constants.Outcome.Default,
                 location=constants.Location.Default,
                 month=constants.Month.Default,
                 season_segment=constants.SeasonSegment.Default,
                 date_from=constants.DateFrom.Default,
                 date_to=constants.DateTo.Default,
                 opponent_team_id=constants.OpponentTeamID.Default,
                 vs_conf=constants.VsConference.Default,
                 vs_div=constants.VsDivision.Default,
                 position=constants.PlayerPosition.Default,
                 game_segment=constants.GameSegment.Default,
                 period=constants.Period.Default,
                 last_n_games=constants.LastNGames.Default,
                 ahead_behind=constants.AheadBehind.Default,
                 context_measure=constants.ContextMeasure.Default,
                 clutch_time=constants.ClutchTime.Default,
                 rookie_year=constants.RookieYear.Default):

        self.json = _get_json(endpoint=self._endpoint,
                              params={'PlayerID': player_id,
                                      'TeamID': team_id,
                                      'GameID': game_id,
                                      'LeagueID': league_id,
                                      'Season':  season,
                                      'SeasonType': season_type,
                                      'Outcome': outcome,
                                      'Location': location,
                                      'Month': month,
                                      'SeasonSegment': season_segment,
                                      'DateFrom':  date_from,
                                      'DateTo': date_to,
                                      'OpponentTeamID': opponent_team_id,
                                      'VsConference': vs_conf,
                                      'VsDivision': vs_div,
                                      'PlayerPosition': position,
                                      'GameSegment': game_segment,
                                      'Period':  period,
                                      'LastNGames': last_n_games,
                                      'AheadBehind': ahead_behind,
                                      'ContextMeasure': context_measure,
                                      'ClutchTime': clutch_time,
                                      'RookieYear': rookie_year})

    def shot_chart(self):
        return _api_scrape(self.json, 0)

    def league_average(self):
        return _api_scrape(self.json, 1)

