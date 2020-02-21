

from subprocess import Popen, run, TimeoutExpired

if __name__=='__main__':
    p1 = Popen(['python3','finnhub_ws.py','SPY','QQQ'],shell=False,stdin=None,stdout=None,stderr=None,close_fds=True)
    p2 = Popen(['python3','iex_ws.py','SPY','QQQ'],shell=False,stdin=None,stdout=None,stderr=None,close_fds=True)
    print('Finnhub Stream PID {}'.format(p1.pid))
    print('IEX TOPS Stream PID {}'.format(p2.pid))
    # Start Live Trading
    p3 = run(['python3','zmq_subscribe.py'],check=True)
    p1.kill()
    p2.kill()
    print('Datastream and live trading stopped')





