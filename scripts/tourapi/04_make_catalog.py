import json
from datetime import date
from pathlib import Path

import pandas as pd


# 프로젝트 루트 자동 탐색
# D:\JDT\scripts\tourapi\04_make_catalog.py -> D:\JDT
ROOT = Path(__file__).resolve().parents[2]

NORMALIZED_FILE = (
    ROOT / "data" / "normalized" / "tourapi_gunsan_normalized.csv"
)

METADATA_DIR = ROOT / "data" / "metadata"
METADATA_FILE = METADATA_DIR / "tourapi_gunsan_metadata.json"

CATALOG_FILE = ROOT / "docs" / "datasets.csv"

METADATA_DIR.mkdir(parents=True, exist_ok=True)
CATALOG_FILE.parent.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 1. 정규화된 인스턴스 CSV 읽기
# --------------------------------------------------

if not NORMALIZED_FILE.exists():
    raise FileNotFoundError(
        f"정규화 CSV가 없습니다.\n"
        f"먼저 03_normalize.py를 실행하세요.\n"
        f"예상 경로: {NORMALIZED_FILE}"
    )

df = pd.read_csv(NORMALIZED_FILE)

row_count = len(df)
unique_count = df["source_id"].nunique()

linking_keys = [
    "K1_name",
    "K2_address",
    "K3_latitude",
    "K4_longitude",
    "K5_category",
]

missing_linking_keys = {}

for col in linking_keys:
    if col in df.columns:
        missing = (
            df[col].isna()
            | (df[col].astype(str).str.strip() == "")
        ).sum()

        missing_linking_keys[col] = int(missing)


# --------------------------------------------------
# 2. JSON 메타데이터 생성
# --------------------------------------------------

metadata = {
    "dataset_id": "TOURAPI-GUNSAN-20261006",

    "title": "한국관광공사 TourAPI 군산시 관광정보",

    "description":
        "한국관광공사 TourAPI에서 수집한 군산시 관광정보를 "
        "프로젝트 공통 규칙에 따라 정규화한 데이터셋",

    "provider": "한국관광공사",

    "source_portal": "공공데이터포털",

    "portal_url":
        "https://www.data.go.kr/data/15101578/openapi.do",

    "api": {
        "service": "KorService2",
        "endpoint": "areaBasedList2",
        "area_code": "37",
        "sigungu_code": "2"
    },

    "license":
        "이용허락범위 제한 없음; "
        "이미지는 공공누리 1유형/3유형 등 개별 조건 확인",

    "retrieved_at": date.today().isoformat(),

    "instance_file":
        "data/normalized/tourapi_gunsan_normalized.csv",

    "format": "CSV",

    "encoding": "UTF-8-SIG",

    "row_count": row_count,

    "unique_count": int(unique_count),

    "primary_key": "source_id",

    "source_primary_key": "contentid",

    "linking_keys": linking_keys,

    "linking_key_missing_count": missing_linking_keys,

    "columns": list(df.columns),

    "notes":
        "전북특별자치도 areaCode=37, "
        "군산시 sigunguCode=2. "
        f"정규화 인스턴스 {row_count}건. "
        f"source_id 고유값 {unique_count}건."
}


with open(
    METADATA_FILE,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        metadata,
        f,
        ensure_ascii=False,
        indent=2
    )


# --------------------------------------------------
# 3. 전체 데이터셋 목록용 CSV도 유지
# --------------------------------------------------

catalog_row = {
    "dataset_id": metadata["dataset_id"],
    "title": metadata["title"],
    "provider": metadata["provider"],
    "portal_url": metadata["portal_url"],
    "api_or_file": "OpenAPI: KorService2/areaBasedList2",
    "license": metadata["license"],
    "retrieved_at": metadata["retrieved_at"],
    "row_count": metadata["row_count"],
    "key_columns": metadata["primary_key"],
    "linking_keys": ";".join(linking_keys),
    "notes": metadata["notes"],
}

catalog_df = pd.DataFrame([catalog_row])

catalog_df.to_csv(
    CATALOG_FILE,
    index=False,
    encoding="utf-8-sig"
)


# --------------------------------------------------
# 결과 출력
# --------------------------------------------------

print("메타데이터 생성 완료")
print("JSON 메타데이터:", METADATA_FILE)
print("인스턴스 CSV:", NORMALIZED_FILE)
print("데이터셋 카탈로그:", CATALOG_FILE)
print()
print("인스턴스 행 수:", row_count)
print("source_id 고유 개수:", unique_count)
print("연결키 결측:", missing_linking_keys)