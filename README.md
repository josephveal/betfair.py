betfair.py is a Python wrapper for the Betfair API. It supports all betting and account
api's for both the UK and Australian wallets. 


Installation
------------

::

    $ pip install betfair.py

Requirements
------------

- Python >= 2.7 or >= 3.3

Testing
-------

To run tests ::

    $ py.test

SSL Certificates
----------------

For non-interactive login, you must generate a self-signed SSL certificate
and upload it to your Betfair account. Betfair.py includes tools for
simplifying this process. To create a self-signed certificate, run ::

    invoke ssl

This will generate a file named ``betfair.pem`` in the ``certs`` directory.
You can write SSL certificates to another directory by passing the
``--name`` parameter ::

    invoke ssl --name=path/to/certs/ssl

This will generate a file named ``ssl.pem`` in the ``path/to/certs/``
directory. Once you have generated the SSL certificate, you can upload the
.pem file to Betfair at https://myaccount.betfair.com/accountdetails/mysecurity?showAPI=1.

Examples
--------

Create a Betfair client, login, keep alive ping, then logout: 

```python
    from betfair import Betfair
    client = Betfair("QWERTYasdfzxcv", "certs/betfair.pem")
    client.login("username", "password")

    client.keep_alive()

    client.logout()
```

List next ten horse racing markets:

```python
    from betfair import Betfair
    from betfair.models import MarketFilter, TimeRange
    from betfair.constants import *
    from betfair.bfhelpers import *

    # login
    # ...

    date_from = datetime.datetime.now().isoformat()
    date_to = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
    time_range = TimeRange(from_=date_from, to=date_to)
    market_filter = MarketFilter(
        event_type_ids=["7"], market_start_time=time_range, market_type_codes=["WIN"])
    
    catalogue_list = client.list_market_catalogue(
        horse_race_projection(), max_results=10)

    for catalogue in catalogue_list:
        print "%s %s" % (catalogue.market_id, catalogue.market_name)
        for runner in catalogue.runners:
            print "  %s %s" % (runner.selection_id, runner.runner_name) 
```

Bet on a horse: 

```python
    market_id = ...
    selection_id = ...

    limit_order = LimitOrder(size=5.0, price=1.02, persistence_type=PersistenceType.LAPSE)
    place_instructions = PlaceInstruction(
        order_type=OrderType.LIMIT,
        selection_id=selection_id,
        side=Side.LAY,
        limit_order=limit_order)

    place_execution_report = client.place_orders(market_id, [place_instructions])

    bet = place_execution_report.instruction_reports[0]
    print "%s %s %s" % (str(bet.bet_id), str(bet.average_price_matched), str(bet.size_matched))
```

Get Betfair account balance: 

```python
    account_funds = client.get_account_funds(Wallet.AUSTRALIAN)
    print "Available to bet: " + str(account_funds.available_to_bet_balance)
```

Author
------

Forked from: github.com/jmcarp/betfair.py Joshua Carp (jmcarp)
Joel Pobar

License
-------

MIT licensed. See the bundled `LICENSE <https://github.com/jmcarp/betfair.py/blob/master/LICENSE>`_ file for more details
