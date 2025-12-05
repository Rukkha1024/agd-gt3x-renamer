"""
Verify dateOfBirth Ticks conversion
"""
import datetime


def ticks_to_datetime(ticks):
    """Convert Ticks to datetime"""
    base = datetime.datetime(1, 1, 1)
    dt = base + datetime.timedelta(microseconds=int(ticks) / 10)
    return dt


def datetime_to_ticks(dt):
    """Convert datetime to Ticks"""
    base = datetime.datetime(1, 1, 1)
    delta = dt - base
    ticks = int(delta.total_seconds() * 10_000_000)
    return ticks


# Modified 파일의 dateOfBirth 값
ticks_value = 630770112000000000

# Ticks를 datetime으로 변환
converted_date = ticks_to_datetime(ticks_value)
print(f"Ticks: {ticks_value}")
print(f"Converted to datetime: {converted_date}")
print(f"Date only: {converted_date.date()}")

# 1999-11-01로 역계산
test_date = datetime.datetime(1999, 11, 1)
recalculated_ticks = datetime_to_ticks(test_date)
print(f"\n1999-11-01 to Ticks: {recalculated_ticks}")
print(f"Match: {recalculated_ticks == ticks_value}")
