###
# Single Asset Trading 
#
###


import pandas as pd 
import numpy as np
import pickle 
import os, time

class Strategy():

    def __init__(self,multiasset=False,datasets='GBPUSD',debug=False):

        self.datasets = datasets
        self.multiasset = multiasset

        # setup pnl
        if not self.multiasset:
            self.pnl = [] 
            self.holdings = []
            self.period = []
            self.startcash = 100 
            self.cash = self.startcash 
            self.holding = 0
            self.target = 0
            self.lastbid = 0
            self.lastask = 0
            print('Running Pedlar Demo for single asset. Dataset {}'.format(self.datasets))

        else:
            if debug:
                self.datasets = ['SPY','VIX']
            self.assetno = len(self.datasets)

            self.startcash = 100 
            self.cash = self.startcash 
            self.period = []
            self.pnl = [] 
            self.holdings = [] # list of np.array for holding at each time point  

            self.holding = np.zeros(self.assetno)
            self.target = np.zeros(self.assetno)
            self.lastbid = np.zeros(self.assetno)
            self.lastask = np.zeros(self.assetno)

            
            print('Running Pedlar Demo for multiple asset. Dataset {}'.format(self.datasets))
        
        return None 



    def valuation(self):
        if not self.multiasset:
            if self.holding >=0:
                self.portfolio_value = self.holding * self.lastbid + self.cash 
                self.pnl.append(self.portfolio_value - self.startcash)
                self.holdings.append(self.holding)
                self.period.append(self.lasttime)
            else:
                self.portfolio_value = self.holding * self.lastask + self.cash 
                self.pnl.append(self.portfolio_value - self.startcash)  
                self.holdings.append(self.holding)   
                self.period.append(self.lasttime)  
        return None 

    def rebalance(self):
        if not self.multiasset:
            changes = self.target - self.holding
            if changes >=0:
                self.cash = self.cash - changes * self.lastask 
                self.holding = self.target 
            else:
                self.cash = self.cash - changes * self.lastbid
                self.holding = self.target 
        return None


    # Iterate through single assets 
    def run_single(self,single_data=None,debug=False):
        for row in single_data.itertuples():
            self.lasttime = row[1]
            self.lastbid = np.float(row[2])
            self.lastask = np.float(row[3])
            self.rebalance()
            self.valuation()
            self.target = self.ondata(self.lastbid,self.lastask)
            if debug:
                print('Time {} Bid {} Ask {} Target {} Portfolio {}'.format(self.lasttime,self.lastbid,self.lastask,self.target,self.portfolio_value))


    def run_multiple(self,multiple_data=None,debug=False):
        for row in multiple_data.iterruples():
            # prepare data slice with lookback 
            self.dataslice = None 
            # update data for internal system 
            self.lasttime = row[1]
            self.lastbid = None
            self.lastask = None 
            self.rebalance()
            self.valuation()
            # Need to redefine ondata for multiple assets 
            self.target = self.onhistory(self.dataslice) # target is now an array of target 


    def train(self,debug=False):

        if not self.multiasset:
            self.before_trades()
            # load data 
            mydir = os.path.dirname(__file__)
            filename = os.path.join(mydir, 'data','{}_train.csv'.format(self.datasets))
            train_data = pd.read_csv(filename)
            self.run_single(single_data=train_data)
        else:
            self.before_trades()
            # load data from multiple assets 

            self.run_multiple(multiple_data=train_data)

    
    
    
    ########  Functions to be supplied by user ###############################################
    
    def before_trades(self):
        return None

    def ondata(self,bid,ask):
        holding = np.random.random()
        return holding

    ########  Plot strategy results ########## 

    def plot_pnl(self):
        if not self.multiasset:
            try:
                pd.Series(self.pnl).plot(title='Strategy PnL')
                plt.xlabel('Time')
                plt.ylabel('PnL')
            except NameError:
                pass
        return None 

    def plot_holding(self):
        if not self.multiasset:
            try:
                pd.Series(self.holdings).plot(title='Strategy Holding')
                plt.xlabel('Time')
                plt.ylabel('Holding')
            except NameError:
                pass 
        return None 

    def plot_results(self):
        self.plot_pnl()
        self.plot_holding()
        return None 

    def download_results(self):
        if not self.multiasset:
            Backtest = pd.DataFrame({'Profit':self.pnl,'Holding':self.holdings},index=self.period)
            Backtest.to_csv('Backtest_{}.csv'.format(self.datasets))
        return None 

    def download_train(self,dataset='GBPUSD'):
        mydir = os.path.dirname(__file__)
        filename = os.path.join(mydir, 'data','{}_train.csv'.format(dataset))
        train_data = pd.read_csv(filename)
        train_data.to_csv('Train_{}.csv'.format(dataset))
        print('Training Data Downloaded from dataset {}'.format(dataset))
        return None

    def save(self,name='samplestrat'):
        f = open(name,mode='wb')
        pickle.dump(self,f)
        return None 



if __name__=='__main__':

    time_s = time.time()
    
    strat = Strategy(datasets='GBPUSD')
    strat.train()
    strat.download_results()
    strat.save('Mystrategy')

    f = open('Mystrategy',mode='rb')
    strat2 = pickle.load(f)
    
    print(time.time() - time_s)
