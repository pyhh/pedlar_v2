import pandas as pd 
import numpy as np
import os, pickle, time
import heapq, itertools
from datetime import datetime 
## Namedtuples for saving records 
from collections import namedtuple # type(a).__name__ to get name of a namedtuple 


# pip3 install git+https://github.com/ThomasWong2022/IEXTools.git
# Only works for Python 3.7.0 or above 
try:
    import IEXTools
except:
    pass


# Define records to be printed 
RebalanceRecord = namedtuple('Rebalance',['time','exchange','name','holding','fairvalue','NAV'])


class DataLoader():

    def __init__(self,exchange='IEX',name='GBPUSD',source='csv',train=True):

        self.source = source
        self.name = name 
        self.chunksize = 10000
        self.counter = 0
        self.exchange = exchange
        
        if source=='csv' and train:
            filename = './data/{}_train.csv'.format(name)
            self.dataloader = pd.read_csv(filename,iterator=True)

        if source=='csv' and not train:
            filename = './data/{}_test.csv'.format(name)
            self.dataloader = pd.read_csv(filename,iterator=True)

        if source=='pcap':
            filename = './data/{}.pcap'.format(self.name)
            if '1.5' in self.name:
                protocol = 1.5
            else:
                protocol = 1.6
            self.dataloader = IEXTools.Parser(filename,tops_version=protocol)

    
    def next(self):
        
        if self.source == 'csv' and self.exchange == 'IEX':
            if self.counter % self.chunksize == 0:
                try:
                    self.dfslice = self.dataloader.get_chunk(self.chunksize)
                    self.dfslice['Asset'] = self.name
                    self.dfslice['Exchange'] = self.exchange
                    self.dfslicer = self.dfslice.itertuples(name=self.exchange)
                    data = next(self.dfslicer)
                    self.counter = 1
                except:
                    print('No more data chunk {}'.format(self.name))
                    data = None 
            else:
                try:
                    data = next(self.dfslicer)
                    self.counter += 1   
                except StopIteration:
                    print('No more data {}'.format(self.name))
                    data = None 
            return data

        if self.source == 'pcap' and self.exchange == 'IEX':
            allowed = [IEXTools.messages.QuoteUpdate]
            try:
                data = self.dataloader.get_next_message(allowed)
            except StopIteration:
                data = None
        return data 



class Asset():

    def __init__(self,name='GBPUSD',exchange='IEX'):


        self.name = name 
        self.exchange = exchange
        self.holding = 0
        self.target = 0
        self.oldbid = 0
        self.oldask = 0
        self.newbid = 0
        self.newask = 0

class Portfolio():

    def __init__(self,cash=100000):
        
        self.cash = cash 
        self.profit = 0

# Triats 
class Event():

    def __init__(self,eventtype='Data'):
        self.eventtype = eventtype

    def process(self):
        pass 

class DataEvent():

    def __init__(self,dataloader=None,dataslice=None):
        self.eventtype = 'Data'
        self.dataloader = dataloader
        self.dataslice = dataslice

    # Get next data from file so that it can be processed 
    def process(self):
        nextdata = self.dataloader.next()
        if nextdata:
            if self.dataloader.source == 'csv': # csv files have data in a given format 
                priority = nextdata.Time
            elif self.dataloader.source == 'pcap' and self.dataloader.exchange == 'IEX':
                priority = nextdata.timestamp   ## pcap files have unix timestamp
        else:
            priority = None
        return (priority,nextdata)


class RebalanceEvent():
   
    def __init__(self,portfolio=None,asset=None,priority=None):
        self.eventtype ='Rebalance'
        self.portfolio = portfolio
        self.asset = asset
        self.priority = priority 

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    def process(self):
        # TODO: How to handle missing bid or ask

        # Compute NAV changes for the asset 
        # TODO Do not update changes if bid or ask is missing??
        if self.asset.holding >= 0:
            NAV_change = self.asset.holding * (self.asset.newbid - self.asset.oldbid)
        else:
            NAV_change = self.asset.holding * (self.asset.newask - self.asset.oldask)

        # Update Cash 
        change = self.asset.target - self.asset.holding
        # TODO Raise error if trying to buy(sell) when ask(bid) is missing 
        if change > 0:
            self.portfolio.cash = self.portfolio.cash - change * self.asset.newask
        else:
            self.portfolio.cash = self.portfolio.cash - change * self.asset.newbid

        # Update Transaction cost
        tcost = abs((self.asset.newask - self.asset.newbid) * change)
        # Update NAV 
        self.portfolio.profit= self.portfolio.profit + NAV_change - tcost
    
        # Update Asset Holding 
        # Check tick is valid for updating fairvalue
        self.asset.holding = self.asset.target
        fairvalue = (self.asset.newbid + self.asset.newask)/2
        # Generate record 
        self.record = RebalanceRecord(self.priority,self.asset.exchange,self.asset.name,self.asset.holding,fairvalue,self.portfolio.profit)

        return self.portfolio, self.asset, self.record


class Backtest():

    def __init__(self, exchange='IEX', source='csv', assets=None, 
                    pcaps=None, cash=100000, filename='Backtest.txt'):

        self.outputfile = open(filename,'a') # Output file name
        self.assetnames = assets
        self.pcapnames = pcaps
        self.Portfolio = Portfolio(cash=cash) 

        self.exchange = exchange
        self.source = source 
        
        if self.source == 'csv':
            Assets = [Asset(f,self.exchange) for f in self.assetnames] 
            self.Assets = dict(zip(self.assetnames,Assets)) 
        elif self.source == 'pcap':
            # dynamic dictionary of assets update as in live trading 
            self.Assets = dict()

        self.EventQueue = [] # Priority Queue Private 
        self.EventCounter = itertools.count() # Tie-breaker for Priority Queue Private 

        print('Backtest Start Exchange {} Source {} '.format(exchange,source))

        return None 
    
    def Process_Event(self,event=None,timestamp=None):

        eventtype = event.eventtype
        if eventtype == 'Data':
            # Prase dataslice according to source and exchange 
            if event.dataloader.source == 'csv':
                Current_Asset_Name = event.dataslice.Asset
                Current_Bid = event.dataslice.Bid
                Current_Ask = event.dataslice.Ask
            elif event.dataloader.source == 'pcap' and event.dataloader.exchange == 'IEX':
                Current_Asset_Name = event.dataslice.symbol
                Current_Bid = event.dataslice.bid_price_int / 10000
                Current_Ask = event.dataslice.ask_price_int / 10000
            Current_exchange = event.dataloader.exchange 
            # Current asset if not exist
            Current_Asset = self.Assets.setdefault(Current_Asset_Name,Asset(name=Current_Asset_Name,exchange=Current_exchange))
            # Update assets for latest prices
            Current_Asset.oldbid = Current_Asset.newbid
            Current_Asset.oldask = Current_Asset.newask
            # TODO How to Handle missing bid ask in quotes 
            if Current_Bid >0:
                Current_Asset.newbid = Current_Bid
            if Current_Ask >0:
                Current_Asset.newask = Current_Ask

            # Rebalance 
            NewRebalance = RebalanceEvent(portfolio=self.Portfolio,asset=Current_Asset,priority=timestamp)
            heapq.heappush(self.EventQueue,(timestamp,next(self.EventCounter),NewRebalance))
            
            # generate new data event for backtesting 
            newtime, newdataslice = event.process()
            # Check if there is new data
            if newdataslice:
                NewEvent = DataEvent(dataloader=event.dataloader,dataslice=newdataslice)
                heapq.heappush(self.EventQueue,(newtime,next(self.EventCounter),NewEvent))

            # Get user update target and update Asset attribute 
            Current_Asset.target = self.ondata(event.dataslice)

        if eventtype == 'Rebalance':
            Current_Asset = self.Assets[event.asset.name]
            self.Portfolio, Current_Asset , newrebalancerecord  = event.process()
            self.outputfile.write(newrebalancerecord.__repr__())
            self.outputfile.write('\n')
        return None 

   
    def run(self,train=True, debug=False):

        # Populate EventQueue with data events 
        if self.source == 'csv':
            for name in self.assetnames:
                _loader = DataLoader(name=name,source=self.source,exchange=self.exchange,train=train)
                newdataslice = _loader.next()
                timestamp = newdataslice.Time
                NewEvent = DataEvent(dataloader=_loader,dataslice=newdataslice)
                heapq.heappush(self.EventQueue,(timestamp,next(self.EventCounter),NewEvent))

        if self.source == 'pcap' and self.exchange=='IEX':
            for name in self.pcapnames: ## 
                _loader = DataLoader(name=name,source=self.source,exchange=self.exchange)
                newdataslice = _loader.next()
                timestamp = newdataslice.timestamp
                NewEvent = DataEvent(dataloader=_loader,dataslice=newdataslice)
                heapq.heappush(self.EventQueue,(timestamp,next(self.EventCounter),NewEvent))

        # Run user before trades
        self.before_trades()
        while len(self.EventQueue) > 0:
            current_time, current_counter, current_event = heapq.heappop(self.EventQueue)
            self.Process_Event(current_event,current_time)
            if debug:
                if current_event.eventtype == 'Data':
                    print(current_event.dataslice)
                if current_event.eventtype == 'Rebalance':
                    print(current_event.record)

        self.outputfile.close()

        return None 

    ########  Functions to be supplied by user ###############################################
    
    def before_trades(self):
        import csv 
        fieldnames = ['Time','Bid', 'Ask']
        self.spyfile = open('data/GLD_train.csv','w')
        self.qqqfile = open('data/VXX_train.csv','w')
        self.SPYwriter = csv.DictWriter(self.spyfile, fieldnames=fieldnames)
        self.QQQwriter = csv.DictWriter(self.qqqfile, fieldnames=fieldnames)
        self.SPYwriter.writeheader()
        self.QQQwriter.writeheader()
        self.counter = 0
        return None

    def ondata(self,dataslice):  
        if dataslice.symbol == 'GLD' and self.counter<1000:
            self.SPYwriter.writerow({'Time':dataslice.timestamp,'Bid': dataslice.bid_price_int / 10000, 'Ask': dataslice.ask_price_int / 10000})
            self.counter += 1
        if dataslice.symbol == 'VXX' and self.counter<1000:
            self.QQQwriter.writerow({'Time':dataslice.timestamp,'Bid': dataslice.bid_price_int / 10000, 'Ask': dataslice.ask_price_int / 10000})
            self.counter += 1
        if self.counter >=1000:
            self.spyfile.close()
            self.qqqfile.close()
        holding = np.random.randint(1,10)
        return holding

############################################################################################

    def save(self,name='samplestrat'):
        f = open(name,mode='wb')
        pickle.dump(self,f)
        return None 

###########################################################################################

if __name__=='__main__':

    import sys 

    try:
        test = sys.argv[1]
    except IndexError:
        test = 'csv'

    if test == 'csv':
        time_s = time.time()
        strat = Backtest(assets=['VIX','SPY'],source='csv',exchange='IEX',filename='data/csvbacktest.txt').run(debug=False)
        print(time.time() - time_s)
    elif test == 'iexpcap':
        strat = Backtest(pcaps=['20161212_IEXTP1_TOPS1.5'],source='pcap',exchange='IEX',filename='data/pcapbacktest.txt').run(debug=False)

    
