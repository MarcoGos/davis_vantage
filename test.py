from datetime import datetime, timedelta
# from pyvantagepro import VantagePro2
from pyvantagepro import VantagePro2

def convert_to_celcius(value: float) -> float:
    return round((value - 32.0) * (5.0/9.0), 1)

vp = VantagePro2.from_url('tcp:weatherlink.local:1234')

# end_datetime = datetime.now()
# start_datetime = end_datetime - timedelta(days = 1)
# archives = vp.get_archives(start_datetime, end_datetime)

data = vp.get_hilows()

print(convert_to_celcius(data['TempLoDay']))
print(convert_to_celcius(data['TempHiDay']))
