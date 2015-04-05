# -*- coding: utf-8 -*-

import os
import json
import requests
import itertools
from six.moves import http_client as httplib
from six.moves import urllib_parse as urllib

from . import utils
from . import models
from . import exceptions
from constants import *
from network import Network

class Betfair(object):
    """Betfair API client.

    :param str app_key: Optional application identifier
    :param str cert_file: Path to self-signed SSL certificate file(s); may be
        a *.pem file or a tuple of (*.crt, *.key) files

    """
    def __init__(self, app_key, cert_file, exchange):
        self.app_key = app_key
        self.cert_file = cert_file
        self.exchange = exchange
        self.network_client = Network(app_key)


    # Authentication methods
    def login(self, username, password):
        """Log in to Betfair. Sets `session_token` if successful.

        :param str username: Username
        :param str password: Password
        :raises: BetfairLoginError

        """
        self.network_client.login(username, password)


    @utils.requires_login
    def keep_alive(self):
        """Reset session timeout.

        :raises: BetfairAuthError

        """
        self.network_client.keep_alive()


    @utils.requires_login
    def logout(self):
        """Log out and clear `session_token`.

        :raises: BetfairAuthError

        """
        self.network_client.logout()
        self.network_client.session_token = None


    # Bet query methods
    @utils.requires_login
    def list_event_types(self, filter={}, locale=None):
        """

        :param MarketFilter filter:
        :param str locale:

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            LIST_EVENT_TYPES,
            utils.get_kwargs(locals()))
        return utils.process_result(result, models.EventTypeResult)


    @utils.requires_login
    def list_competitions(self, filter={}, locale=None):
        """

        :param MarketFilter filter:
        :param str locale:

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            LIST_COMPETITIONS,
            utils.get_kwargs(locals()))
        return utils.process_result(result, models.CompetitionResult)


    @utils.requires_login
    def list_time_ranges(self, filter, granularity):
        """

        :param MarketFilter filter:
        :param TimeGranularity granularity:

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            LIST_TIME_RANGES,
            utils.get_kwargs(locals()))
        return utils.process_result(result, models.TimeRangeResult)


    @utils.requires_login
    def list_events(self, filter={}, locale=None):
        """

        :param MarketFilter filter:
        :param str locale:

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            LIST_EVENTS,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.EventResult)


    @utils.requires_login
    def list_market_types(self, filter={}, locale=None):
        """

        :param MarketFilter filter:
        :param str locale:

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            LIST_MARKET_TYPES,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.MarketTypeResult)


    @utils.requires_login
    def list_countries(self, filter={}, locale=None):
        """

        :param MarketFilter filter:
        :param str locale:

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            LIST_COUNTRIES,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.CountryCodeResult)


    @utils.requires_login
    def list_venues(self, filter={}, locale=None):
        """

        :param MarketFilter filter:
        :param str locale:

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            LIST_VENUES,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.VenueResult)


    @utils.requires_login
    def list_market_catalogue(
        self, filter, market_projection=None, sort=None, max_results=10, locale=None):
        """

        :param MarketFilter filter:
        :param list market_projection:
        :param MarketSort sort:
        :param int max_results:
        :param str locale:

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            LIST_MARKET_CATALOGUE,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.MarketCatalogue)


    @utils.requires_login
    def list_market_book(
            self, market_ids, price_projection=None, order_projection=None,
            match_projection=None, currency_code=None, locale=None):
        """

        :param list market_ids: List of market IDs
        :param PriceProjection price_projection:
        :param OrderProjection order_projection:
        :param MatchProjection match_projection:
        :param str currency_code:
        :param str locale:

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            LIST_MARKET_BOOK,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.MarketBook)


    @utils.requires_login
    def list_market_profit_and_loss(
            self, market_ids, include_settled_bets=False,
            include_bsp_bets=False, net_of_commission=False):
        """Retrieve profit and loss for a given list of markets.

        :param list market_ids: List of markets to calculate profit and loss
        :param bool include_settled_bets: Option to include settled bets
        :param bool include_bsp_bets: Option to include BSP bets
        :param bool net_of_commission: Option to return profit and loss net of
            users current commission rate for this market including any special
            tariffs

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            LIST_MARKET_PROFIT_AND_LOSS,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.MarketProfitAndLoss)


    # Chunked iterators for list methods
    def iter_list_market_book(self, market_ids, chunk_size, **kwargs):
        """Split call to `list_market_book` into separate requests.

        :param list market_ids: List of market IDs
        :param int chunk_size: Number of records per chunk
        :param dict kwargs: Arguments passed to `list_market_book`

        """
        return itertools.chain(*(
            self.list_market_book(market_chunk, **kwargs)
            for market_chunk in utils.get_chunks(market_ids, chunk_size)
        ))

    def iter_list_market_profit_and_loss(
            self, market_ids, chunk_size, **kwargs):
        """Split call to `list_market_profit_and_loss` into separate requests.

        :param list market_ids: List of market IDs
        :param int chunk_size: Number of records per chunk
        :param dict kwargs: Arguments passed to `list_market_profit_and_loss`

        """
        return itertools.chain(*(
            self.list_market_profit_and_loss(market_chunk, **kwargs)
            for market_chunk in utils.get_chunks(market_ids, chunk_size)
        ))

    # Betting methods

    @utils.requires_login
    def list_current_orders(
            self, bet_ids = None, market_ids = None, order_projection = None, date_range = None, order_by = None,
            sort_dir = None, from_record = None, record_count = None):
        """

        :param bet_ids:
        :param market_ids:
        :param order_projection:
        :param date_range:
        :param order_by:
        :param sort_dir:
        :param from_record:
        :param record_count:

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            LIST_CURRENT_ORDERS,
            utils.get_kwargs(locals())
        )
        return utils.process_result(result, models.CurrentOrderSummaryReport)


    @utils.requires_login
    def list_cleared_orders(
            self, bet_status, event_type_ids=None, event_ids=None, market_ids=None,
            runner_ids=None, bet_ids=None, side=None, settled_date_range=None, group_by=None,
            include_item_description=None, locale=None, from_record=None, record_count=None):
        """

        :param bet_status:
        :param event_type_ids:
        :param event_ids:
        :param market_ids:
        :param runner_ids:
        :param bet_ids:
        :param side:
        :param settled_date_range:
        :param group_by:
        :param include_item_description:
        :param locale:
        :param from_record:
        :param record_count:

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            LIST_CLEARED_ORDERS,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.ClearedOrderSummaryReport)


    @utils.requires_login
    def place_orders(self, market_id, instructions, customer_ref=None):
        """Place new orders into market. This operation is atomic in that all
        orders will be placed or none will be placed.

        :param str market_id: The market id these orders are to be placed on
        :param list instructions: List of `PlaceInstruction` objects
        :param str customer_ref: Optional order identifier string

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            PLACE_ORDERS,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.PlaceExecutionReport)


    @utils.requires_login
    def cancel_orders(self, market_id, instructions, customer_ref=None):
        """Cancel all bets OR cancel all bets on a market OR fully or
        partially cancel particular orders on a market.

        :param str market_id: If not supplied all bets are cancelled
        :param list instructions: List of `CancelInstruction` objects
        :param str customer_ref: Optional order identifier string

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            CANCEL_ORDERS,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.CancelExecutionReport)


    @utils.requires_login
    def replace_orders(self, market_id, instructions, customer_ref=None):
        """This operation is logically a bulk cancel followed by a bulk place.
        The cancel is completed first then the new orders are placed.

        :param str market_id: The market id these orders are to be placed on
        :param list instructions: List of `ReplaceInstruction` objects
        :param str customer_ref: Optional order identifier string

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            REPLACE_ORDERS,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.ReplaceExecutionReport)


    @utils.requires_login
    def update_orders(self, market_id, instructions, customer_ref=None):
        """Update non-exposure changing fields.

        :param str market_id: The market id these orders are to be placed on
        :param list instructions: List of `UpdateInstruction` objects
        :param str customer_ref: Optional order identifier string

        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Betting,
            UPDATE_ORDERS,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.UpdateExecutionReport)


    # account api
    @utils.requires_login
    def get_account_funds(self, wallet=None):
        """Get the current funds in an account
        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Account,
            GET_ACCOUNT_FUNDS,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.AccountFundsResponse)

    @utils.requires_login
    def get_account_statement(self, locale=None, from_record=None, record_count=None,
            item_date_range=None, include_item=None, wallet=None):
        """Get the account statement

        :param str locale: the language to be used
        :param int from_record: specifies the first record to be returned
        :param int record_count: the maximum number of records to be returned
        :param TimeRange item_date_range: return items within this time range
        :param IncludeItem include_item: which items to include
        :param Wallet wallet: specify which wallet
        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Account,
            GET_ACCOUNT_STATEMENT,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.AccountStatementReport)

    @utils.requires_login
    def get_account_details(self):
        """Get the account details
        """
        result = self.network_client.invoke_sync(
            self.exchange,
            Endpoint.Account,
            GET_ACCOUNT_DETAILS,
            utils.get_kwargs(locals()))

        return utils.process_result(result, models.AccountDetailsResponse)

