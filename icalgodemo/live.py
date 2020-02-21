###
# Live Trading
#
###
import zmq

import pandas as pd 
import numpy as np
import os, time, json, datetime
from subprocess import Popen, run, TimeoutExpired

class LiveTrading():

    def __init__(self,counter=500,filename='data/live.txt',tickers=None,debug=False,Finnhub_key=None):

        self.FINNHUB_KEY = Finnhub_key
        self.tickers = tickers 
        self.tcpport = 'tcp://127.0.0.1:7000'

        self.maxdata = counter 
        self.debug = debug
        self.outputfile = open(filename,'a')

        # Output target holdings from users
        self.newexchange = []
        self.newasset = []
        self.newtarget = []

        # Internal dictionarties to keep track of the holdings and prices of the assets
        self.holding = dict()
        self.fairvalue = dict()
        
        self.cash = 100000
        self.portfolio_value = 100000 
        self.tcost_ratio = 0.0015

        # Setup socket 
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.bind(self.tcpport)
        # Subscrube to all channels by default 
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')

    def rebalance(self):
        assert len(self.newexchange) == len(self.newasset)
        assert len(self.newexchange) == len(self.newtarget)

        for i in range(0,len(self.newexchange)):
            current_holding = self.holding.setdefault(self.newexchange[i],dict()).get(self.newasset[i],0)
            change = self.newtarget[i] - current_holding
            fv = self.fairvalue.setdefault(self.newexchange[i],dict()).get(self.newasset[i],0)
            # Rebalance rules 
            self.cash = self.cash - change * fv - abs(change) * fv * self.tcost_ratio
            # Set holding 
            self.holding.setdefault(self.newexchange[i],dict())[self.newasset[i]] = self.newtarget[i]
        return None

    def valuation(self):
        # Write time 
        reftime = datetime.datetime.now().isoformat()
        self.outputfile.write(reftime)
        # Write Cash 
        self.outputfile.write(' Cash {}'.format(self.cash))
        # Write Asset holding and fairvalue 
        self.portfolio_value = self.cash 
        for exchange,exchange_value in self.holding.items():
            for asset,holding in exchange_value.items():
                FV = self.fairvalue.setdefault(exchange,dict()).get(asset,0)
                self.outputfile.write(' {} {} {} {} '.format(exchange,asset,holding,FV))
                self.portfolio_value += FV * holding
        # Write portfolio value 
        self.outputfile.write('\n')
        self.outputfile.write(reftime)
        self.outputfile.write(' NAV {}'.format(self.portfolio_value))
        # Compute other metrics?? 
        self.outputfile.write('\n')

    def parse_data(self,exchange,tickdata):
        if (exchange == 'IEX') or (exchange == 'Finnhub') :
            try:
                d = json.loads(tickdata)
                if self.debug:
                    pass
                    # print(d)
                # Compute FairValue 
                if exchange == 'Finnhub':
                    ticker = d['data'][0]['s']
                    fv = d['data'][0]['p']
                    # No bid ask given by Finnhub so uses default values 

                if exchange == 'IEX':
                    ticker = d['symbol']
                    if d['askPrice'] <=0:
                        fv = d['lastSalePrice']
                    else:
                        fv = (d['bidPrice']+d['askPrice']) / 2
                        # Set t-cost ratio 
                        self.tcost_ratio = (d['askPrice'] - d['bidPrice'])/fv
                # Update FairValue 
                self.fairvalue.setdefault(exchange,dict())[ticker] = fv
            except json.decoder.JSONDecodeError:
                print('Not decoded ', tickdata)
                return None,0

        return exchange,d

    def ondata(self,exchange,tickdata):
        # Prase data 
        exchange,d = self.parse_data(exchange,tickdata)
        if exchange is None:
            print('Invalid tickdata')
        else:
            # Rebalance 
            self.rebalance()
            self.valuation()
            # Get target from user 
            self.newexchange, self.newasset, self.newtarget = self.set_target(exchange,d) 
  

    ### Main event loop of going through messages from combined streams 
    def run(self):
        counter = 0
        self.before_trades()
        datastreams = self.start_datastream()
        while counter <= self.maxdata:
            message = self.socket.recv_multipart()
            exchange = message[0].decode()
            tick = message[1]
            self.ondata(exchange,tick)
            counter += 1
        # Close file and datastreams
        for p in datastreams:
            p.kill()
        self.outputfile.close()


    ########  Functions to be supplied by user ###############################################
    
    def before_trades(self):
        return None

    '''
    Input:  exchange: String, name of exchange
            tick: dictionary, content of a tick, structure depending on exchange 
    Output: exchanges: List<String>, tickers: List <String>, targets: List<f64> of equal length
    '''
    def set_target(self,exchange,tick):
        holding = np.random.randint(1,10)
        return ['Finnhub'] , ['BINANCE:BTCUSDT'], [holding]

    def start_datastream(self):

        mydir = os.path.dirname(__file__)
        finnhubfilename = os.path.join(mydir, 'Datastream','finnhub_ws.py')
        iexfilename = os.path.join(mydir, 'Datastream','iex_ws.py')
        finnhubstream = ['python3',finnhubfilename] 
        iexstream = ['python3',iexfilename ,'TOPS'] 
        finnhubstream.extend([self.FINNHUB_KEY])
        finnhubstream.extend(self.tickers)
        iexstream.extend(self.tickers)
        iexstream.extend(['SPY','QQQ'])
        finnhubstream.extend(['BINANCE:BTCUSDT'])
        # Get correct locations for scripts 
        p1 = Popen(finnhubstream,shell=False,close_fds=True)
        p2 = Popen(iexstream,shell=False,close_fds=True)
        print('Finnhub Stream PID {}'.format(p1.pid))
        print('IEX TOPS Stream PID {}'.format(p2.pid))
        return [p1,p2]


    ###############################################################################

if __name__=='__main__':

    # Prase input arguments 

    import sys 

    try:
        finnhub = sys.argv[1]
    except IndexError:
        finnhub = None 
    tickers = sys.argv[2:]

    LiveAgent = LiveTrading(tickers=tickers,debug=True,Finnhub_key=finnhub)
    LiveAgent.run()
