import json
import re
import unicodedata
from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    r"D:\JDT\data\raw\tourapi\tourapi_gunsan_all.json"
)

OUTPUT_DIR = Path(
    r"D:\JDT\data\normalized"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "tourapi_gunsan_normalized.csv"


# TourAPI contentTypeId → 우리 프로젝트에서 사용할 넓은 분류
CONTENT_TYPE_MAP = {
    "12": "tourist_attraction",
    "14": "cultural_facility",
    "15": "event",
    "25": "travel_course",
    "28": "leisure_sports",
    "32": "accommodation",
    "38": "shopping",
    "39": "food",
}


def normalize_text(value):
    if value is None:
        return ""

    value = str(value)

    # 한글 유니코드 형식 통일
    value = unicodedata.normalize("NFC", value)

    # 앞뒤 공백 제거
    value = value.strip()

    # 연속 공백 하나로 통일
    value = re.sub(r"\s+", " ", value)

    return value


def normalize_name(value):
    value = normalize_text(value)

    # 매핑용 이름은 내부 공백도 제거
    # 예: "군산 근대 역사 박물관" → "군산근대역사박물관"
    return value.replace(" ", "")


def normalize_address(addr1, addr2):
    addr1 = normalize_text(addr1)
    addr2 = normalize_text(addr2)

    combined = f"{addr1} {addr2}".strip()

    return normalize_text(combined)


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw = json.load(f)

items = raw["items"]

rows = []

for item in items:

    content_type_id = str(item.get("contenttypeid", ""))

    name = normalize_text(item.get("title", ""))

    address = normalize_address(
        item.get("addr1", ""),
        item.get("addr2", "")
    )

    normalized_name = normalize_name(name)

    normalized_address = address

    latitude = item.get("mapy", "")
    longitude = item.get("mapx", "")

    normalized_category = CONTENT_TYPE_MAP.get(
        content_type_id,
        "other"
    )

    row = {
        # 출처 정보
        "source": "TOUR_API",
        "source_id": item.get("contentid", ""),

        # 원본/표준 장소명
        "name": name,
        "normalized_name": normalized_name,

        # 원본/표준 주소
        "address": address,
        "normalized_address": normalized_address,

        # 위치
        "latitude": latitude,
        "longitude": longitude,

        # 분류
        "contenttypeid": content_type_id,
        "cat1": item.get("cat1", ""),
        "cat2": item.get("cat2", ""),
        "cat3": item.get("cat3", ""),
        "normalized_category": normalized_category,

        # 행정구역
        "area_code": item.get("areacode", ""),
        "sigungu_code": item.get("sigungucode", ""),
        "zipcode": item.get("zipcode", ""),

        # 추적용
        "created_time": item.get("createdtime", ""),
        "modified_time": item.get("modifiedtime", ""),

        # 이미지 출처/저작권 확인용
        "first_image": item.get("firstimage", ""),
        "copyright_type": item.get("cpyrhtDivCd", ""),

        # 5대 연결키
        "K1_name": normalized_name,
        "K2_address": normalized_address,
        "K3_latitude": latitude,
        "K4_longitude": longitude,
        "K5_category": normalized_category,
    }

    rows.append(row)


df = pd.DataFrame(rows)

# Excel에서 한글 안 깨지도록 UTF-8-SIG
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


print("정규화 완료")
print("전체 행 수:", len(df))
print("source_id 고유 개수:", df["source_id"].nunique())
print()
print("카테고리 분포:")
print(df["normalized_category"].value_counts())
print()

print("연결키 결측치:")
for col in [
    "K1_name",
    "K2_address",
    "K3_latitude",
    "K4_longitude",
    "K5_category"
]:
    missing = (
        df[col].isna()
        | (df[col].astype(str).str.strip() == "")
    ).sum()

    print(f"{col}: {missing}건")

print()
print("저장 위치:", OUTPUT_FILE)