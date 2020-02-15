# pedlar_v2
New version of pedlar, the trading platform for Imperial Algosoc 

## strategy 
strategy is used to perform simple backtesting for single/multiple assets. Time Series is assumed to be aligned 

## Backtest 
Backtest is a prototype for simulating trades from any data sources. It runs an event loop which handles data and order events 

Backtest files follow the following format 
csv: Each file is named {ticker}_train.csv {ticker}_test.csv with column Time,Bid,Ask
pcap: IEX pcap files TOPS / DEEP 

## Live 
Live trading using websockets data on US Equities and Forex from IEX and Finnhub  

A live trading agent has a function create datastream which will run each websockets from different sources and poll together through zeromq. 

### Contributors 

Head of Technology: Thomas Wong  

Developers: Lucien Viala 
