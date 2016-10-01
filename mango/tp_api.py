import requests
import json
from config import TRAVEL_PAYOUTS_TOKEN
from datetime import datetime

headers = {"X-Access-Token": TRAVEL_PAYOUTS_TOKEN}

params = {
    "currency": "rub",
    "page": 1,
    "limit": 100,
    "show_to_affiliates": "true",
    "sorting": "price",
    "trip_class": 0,
    "period_type":"month",
    "one_way":"false",
    "beginning_of_period":"2016-12-1"
}
req_base = "http://api.travelpayouts.com/v2/prices/latest"
rp = []
for k, v in params.items():
    rp.append(str(k)+'='+str(v))
req = req_base+"?"+"&".join(rp)+"&origin=MOW&destination=AHO"
print(req)

response = requests.get(req, headers=headers)

dd_in = datetime(2016, 12, 12)
dd_out = datetime(2016, 12, 31)
rd_in =  datetime(2017, 1, 20)
rd_out = datetime(2016, 12, 22)

for f in json.loads(response.text)['data']:
    print (f)
    print()
    dd=datetime.strptime(f['depart_date'],'%Y-%m-%d')
    #if dd>=dd_in and dd<=dd_out:
    #print(dd)