import os
import requests
from dotenv import load_dotenv

load_dotenv(r"D:\JDT\.env")

API_KEY = os.getenv("TOUR_API_KEY")

url = "https://apis.data.go.kr/B551011/KorService2/areaCode2"

params = {
    "serviceKey": API_KEY,
    "MobileOS": "ETC",
    "MobileApp": "JDT",
    "_type": "json",
    "numOfRows": 100,
    "pageNo": 1,

    # 전북특별자치도
    "areaCode": "37"
}

response = requests.get(url, params=params, timeout=30)

print("HTTP 상태:", response.status_code)
print(response.text)