import os
import json
import math
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(r"D:\JDT\.env")

API_KEY = os.getenv("TOUR_API_KEY")

BASE_URL = "https://apis.data.go.kr/B551011/KorService2"
URL = f"{BASE_URL}/areaBasedList2"

AREA_CODE = "37"
SIGUNGU_CODE = "2"

NUM_OF_ROWS = 100

RAW_DIR = Path(r"D:\JDT\data\raw\tourapi")
RAW_DIR.mkdir(parents=True, exist_ok=True)

all_items = []
page_no = 1
total_count = None

while True:
    params = {
        "serviceKey": API_KEY,
        "MobileOS": "ETC",
        "MobileApp": "JDT",
        "_type": "json",
        "areaCode": AREA_CODE,
        "sigunguCode": SIGUNGU_CODE,
        "numOfRows": NUM_OF_ROWS,
        "pageNo": page_no,
        "arrange": "A",
    }

    response = requests.get(URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    header = data["response"]["header"]

    if header["resultCode"] != "0000":
        raise RuntimeError(
            f"API 오류: {header['resultCode']} / {header['resultMsg']}"
        )

    body = data["response"]["body"]

    if total_count is None:
        total_count = body["totalCount"]
        total_pages = math.ceil(total_count / NUM_OF_ROWS)

        print(f"전체 건수: {total_count}")
        print(f"전체 페이지: {total_pages}")

    # 각 페이지 원본 그대로 저장
    page_path = RAW_DIR / f"tourapi_gunsan_page_{page_no:03d}.json"

    with open(page_path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    items = body.get("items", {})

    if items:
        page_items = items.get("item", [])
    else:
        page_items = []

    all_items.extend(page_items)

    print(
        f"{page_no}/{total_pages} 페이지 완료 "
        f"- 현재 {len(all_items)}건"
    )

    if page_no >= total_pages:
        break

    page_no += 1

# contentid 기준 중복 확인
unique_items = {}

for item in all_items:
    content_id = item["contentid"]
    unique_items[content_id] = item

deduplicated_items = list(unique_items.values())

combined = {
    "source": "Korea Tourism Organization TourAPI",
    "api": "areaBasedList2",
    "areaCode": AREA_CODE,
    "sigunguCode": SIGUNGU_CODE,
    "totalCount": total_count,
    "collectedCount": len(all_items),
    "uniqueCount": len(deduplicated_items),
    "items": deduplicated_items,
}

combined_path = RAW_DIR / "tourapi_gunsan_all.json"

with open(combined_path, "w", encoding="utf-8") as f:
    json.dump(
        combined,
        f,
        ensure_ascii=False,
        indent=2
    )

print()
print("수집 완료")
print("API totalCount :", total_count)
print("수집 건수      :", len(all_items))
print("고유 contentid :", len(deduplicated_items))
print("저장 위치      :", combined_path)