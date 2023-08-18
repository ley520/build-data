import requests

headers = {
    "content-type": "application/json;Accept-Charset:utf-8;",
}

params = {
    "lng": "116.4815444946289",
    "orderId": "1010029689746",
    "openId": "o0uhA5VAjDvM_n2l2_p2CV-DC5P8",
    "_ver": "3.7.0",
    "cityId": "42",
    "userId": "5086052997",
    "uuid": "BC4FF6C13283310A508378B3A20C752FCD7AC03B8E7F34D74046A1526B7FC040",
    "platform": 1,
    "lat": "40.0077018737793",
    "token": "AgG-IWbTm8DXROac2jKIrW9h0gCKGbBHfZio2blffIZIW2562b2w7VeNo6BeTm0JVyqWCj2tXIF4MgAAAADQSwcAth-MLGtN8Y6z0KTIeKl2hkFhFOWGzGyIbzvf4zPEZWYjhi99tm2tQxMjwzzvmIOd",
    "status": 1,
}
response = requests.get(
    "http://10.48.151.68:8080/peppermall/order/center/list?_ver=3.22.17",
    params=params,
    headers=headers,
)
print(response.json())
