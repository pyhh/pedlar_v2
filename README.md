# pedlar_v2
New version of pedlar, the trading platform for Imperial Algosoc. 
A python package is provided  

'''
pip install -i https://test.pypi.org/simple/ icalgosocdemo
'''

## Repo Structure (As of 2020 Feb 15) 
Notebook is the folder where documentations on how to use the package is provided  
icalgodemo is the folder where the source code for the trading engine can be found  
Datastream is the folder where examples scripts on using websockets and zeromq can be found. 
The datastreams are needed for live trading.  

### Strategy 
Strategy is used for demo trading ideas in weekly meetings of Algosoc with a few preloaded datasets
Only simple trading strategies are supported. For advanced backtesting plaese refer to the Backtest section. 

### Backtest 
Backtest is a prototype for simulating trades from any data sources. It runs an event loop which handles data and order events. 
It supports lazy loading of data which allows backtesting for tick data. 

Currenly only support data files follow the following format 
csv: Each file is named {ticker}_train.csv {ticker}_test.csv with column Time,Bid,Ask
pcap: IEX pcap files TOPS / DEEP 

### Live 
Live trading using websockets data on US Equities and Forex from IEX and Finnhub  
A live trading agent has a function create datastream which will run each websockets from different sources and poll together through zeromq. 

## Contributors 

Head of Technology: Thomas Wong  

Developers: Lucien Viala 


