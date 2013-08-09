import datetime
import pickle
from pheme.anonymize.termcache import TermCache

def test_termcache():
    tc = TermCache()
    tc['t'] = True
    assert ('t' in tc)

def test_datetime():
    tc = TermCache()
    now = datetime.datetime.now()
    tc[now] = now + datetime.timedelta(seconds=10)
    assert(now in tc)
