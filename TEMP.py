# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 10:59:33 2015

@author: JoeChittenden-Veal
"""
from betfair import Betfair
from betfair.models import MarketFilter, TimeRange
from betfair.constants import *
from betfair.bfhelpers import *

client = Betfair('DaDLQsvPTQXGfWTq', 'certs/betfair.crt',"") #Unsure about use of "exchange" here
client.login("josephveal","H4shS4lt")
##
client.keep_alive


catalogue_list = client.list_market_catalogue(
   soccer_match_odds_filter(), soccer_projection(), max_results=100)

for catalogue in catalogue_list:
    print "%s %s" % (catalogue.market_id, catalogue.market_name)
    for runner in catalogue.runners:
        print "  %s %s" % (runner.selection_id, runner.runner_name)

        
#
#event_type_list = client.list_event_types()
#
#for event_type_result in event_type_list:
#    print "%s %s" % (event_type_result.event_type.id, event_type_result.event_type.name)
#

#market_type_list = client.list_market_types(MarketFilter(event_type_ids=["1"], market_start_time=time_range_48()))
#
#for market_type_result in market_type_list:
#    print "%s %s" % (market_type_result.market_type, market_type_result.market_count)


market_book = client.list_market_book(['1.118300217'])
for market in market_book:
    print market.market_id
    print market.status
    print market.total_matched
    for runner in market_book[0].runners:
        print runner.selection_id
        print runner.status
        print runner.last_price_traded
        for price in runner.ex:
            print price.available_to_back
            print price.available_to_lay
            print price.traded_volume