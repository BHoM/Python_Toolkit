from datetime import datetime

def ticks():
    """Return the number of ticks since 0001:01:01 00:00:00"""
    return int((datetime.utcnow() - datetime(1, 1, 1)).total_seconds())