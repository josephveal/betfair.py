import datetime
from models import *
from constants import *


def horse_race_filter(countries_list=[]):
    market_filter = MarketFilter(
        event_type_ids=["7"],
        market_countries=countries_list,
        market_start_time=time_range_24(),
        market_type_codes=["WIN"])
    return market_filter


def horse_race_projection():
    projection = [MarketProjection.RUNNER_METADATA, MarketProjection.MARKET_DESCRIPTION, MarketProjection.EVENT]
    return projection


def horse_race_price_projection():
    price_data = [PriceData.EX_TRADED, PriceData.EX_ALL_OFFERS]
    price_projection = PriceProjection()
    price_projection.price_data = price_data
    return price_projection

def soccer_match_odds_filter(countries_list=[]):
    market_filter =MarketFilter(
        event_type_ids=["1"],
        market_countries=countries_list,
        market_start_time=time_range_48(),
        market_type_codes=["MATCH_ODDS"])
    return market_filter

#TODO
def soccer_projection():
    projection = [MarketProjection.RUNNER_METADATA, MarketProjection.MARKET_DESCRIPTION, MarketProjection.EVENT]
    return projection

def time_range_24():
    f = datetime.datetime.now().isoformat()
    t = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
    time_range = TimeRange(from_=f, to=t)
    return time_range    

def time_range_48():
    f = datetime.datetime.now().isoformat()
    t = (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()
    time_range = TimeRange(from_=f, to=t)
    return time_range    