from pathlib import Path
from datetime import date

import pandas as pd


OUTPUT = Path(r"D:\JDT\docs\datasets.csv")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

row = {
    "dataset_id": "TOURAPI-GUNSAN-20261006",

    "title": "한국관광공사 TourAPI 군산시 관광정보",

    "provider": "한국관광공사",

    "portal_url":
        "https://www.data.go.kr/data/15101578/openapi.do",

    "api_or_file":
        "OpenAPI: KorService2/areaBasedList2",

    "license":
        "이용허락범위 제한 없음; "
        "이미지는 공공누리 1유형/3유형 등 개별 조건 확인",

    "retrieved_at":
        date.today().isoformat(),

    "row_count": 115,

    "key_columns":
        "contentid",

    "linking_keys":
        "K1_name;"
        "K2_address;"
        "K3_latitude;"
        "K4_longitude;"
        "K5_category",

    "notes":
        "전북특별자치도 areaCode=37, "
        "군산시 sigunguCode=2. "
        "areaBasedList2 전체 115건 수집. "
        "contentid 중복 0건. "
        "5대 연결키 결측 0건."
}

df = pd.DataFrame([row])

df.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig"
)

print("데이터 카탈로그 작성 완료")
print("저장 위치:", OUTPUT)
print()
print(df.to_string(index=False))