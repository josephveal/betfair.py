import datetime
from models import *
from constants import *

def horse_race_filter(countries_list=None):
    from_ = datetime.datetime.now().isoformat()
    to = from_ + datetime.timedelta(days=2).isoformat()
    time_range = TimeRange(from_, to)
    market_filter = MarketFilter(
        event_type_ids=["7"],
        market_countries=countries_list,
        market_start_time=time_range,
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
