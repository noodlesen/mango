import requests
import json
from config import TRAVEL_PAYOUTS_TOKEN
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
    "beginning_of_period":"2017-07-1"
}
req_base = "http://api.travelpayouts.com/v2/prices/latest"
rp = []
for k, v in params.items():
    rp.append(str(k)+'='+str(v))
req = req_base+"?"+"&".join(rp)+"&origin=MOW&destination=PKC"
print(req)

response = requests.get(req, headers=headers)
for f in json.loads(response.text)['data']:
    print (f)