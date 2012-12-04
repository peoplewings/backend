import datetime

def unix_time(dt):
    epoch = dt
    print epoch
    delta = dt - epoch
    return delta.total_seconds()

def unix_time_millis(dt):
    return unix_time(dt) * 1000.0
