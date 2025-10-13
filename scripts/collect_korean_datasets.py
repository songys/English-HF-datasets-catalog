#!/usr/bin/env python3
"""
허깅페이스에서 한국어 데이터셋을 수집하고 정리하는 스크립트
"""
import json
import os
from datetime import datetime
from typing import List, Dict
import pandas as pd
from huggingface_hub import HfApi, list_datasets
from tqdm import tqdm


def collect_korean_datasets() -> List[Dict]:
    """허깅페이스에서 한국어 데이터셋을 수집합니다."""
    api = HfApi()
    datasets = []

    print("한국어 데이터셋 수집 중...")

    # 한국어 태그가 있는 데이터셋 검색
    try:
        for dataset in tqdm(list_datasets(language="ko", full=True)):
            try:
                dataset_info = {
                    "id": dataset.id,
                    "author": dataset.author,
                    "created_at": str(dataset.created_at) if dataset.created_at else None,
                    "last_modified": str(dataset.last_modified) if dataset.last_modified else None,
                    "downloads": dataset.downloads if hasattr(dataset, 'downloads') else 0,
                    "likes": dataset.likes if hasattr(dataset, 'likes') else 0,
                    "tags": list(dataset.tags) if dataset.tags else [],
                    "description": dataset.description if hasattr(dataset, 'description') else "",
                    "url": f"https://huggingface.co/datasets/{dataset.id}",
                    "languages": [],
                    "tasks": [],
                    "size_categories": []
                }

                # 태그에서 언어, 작업, 크기 정보 추출
                if dataset.tags:
                    for tag in dataset.tags:
                        if tag.startswith("language:"):
                            dataset_info["languages"].append(tag.replace("language:", ""))
                        elif tag.startswith("task_categories:"):
                            dataset_info["tasks"].append(tag.replace("task_categories:", ""))
                        elif tag.startswith("size_categories:"):
                            dataset_info["size_categories"].append(tag.replace("size_categories:", ""))

                # 한국어 필터링: 한국어를 포함하고 언어 수가 100개 이하인 데이터셋
                if "ko" in dataset_info["languages"]:
                    # 한국어 포함 + 최대 100개 언어
                    if len(dataset_info["languages"]) <= 100:
                        datasets.append(dataset_info)
            except Exception as e:
                print(f"데이터셋 처리 오류 {dataset.id}: {e}")
                continue

    except Exception as e:
        print(f"데이터셋 목록 가져오기 오류: {e}")

    return datasets


def process_and_save_datasets(datasets: List[Dict], output_dir: str = "docs/data"):
    """데이터셋 정보를 처리하고 JSON 파일로 저장합니다."""
    os.makedirs(output_dir, exist_ok=True)
    archive_dir = os.path.join(output_dir, "archive")
    os.makedirs(archive_dir, exist_ok=True)

    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d")

    # 현재 데이터 구조
    current_data = {
        "last_updated": current_time.isoformat(),
        "total_count": len(datasets),
        "datasets": datasets
    }

    # 1. 현재 데이터를 archive에 저장 (날짜별)
    archive_file = os.path.join(archive_dir, f"korean_datasets_{timestamp}.json")
    with open(archive_file, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, ensure_ascii=False, indent=2)
    print(f"아카이브 저장: {archive_file}")

    # 2. 최신 데이터를 메인 파일로 저장
    output_file = os.path.join(output_dir, "korean_datasets.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, ensure_ascii=False, indent=2)

    print(f"\n총 {len(datasets)}개의 데이터셋 정보를 저장했습니다.")
    print(f"파일 위치: {output_file}")

    # 3. CSV 파일로도 저장 (백업용)
    if datasets:
        df = pd.DataFrame(datasets)
        csv_file = os.path.join(output_dir, "korean_datasets.csv")
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"CSV 파일: {csv_file}")

        # 아카이브 CSV도 저장
        archive_csv = os.path.join(archive_dir, f"korean_datasets_{timestamp}.csv")
        df.to_csv(archive_csv, index=False, encoding='utf-8-sig')

    return output_file


def generate_statistics(datasets: List[Dict]) -> Dict:
    """데이터셋 통계 정보를 생성합니다."""
    stats = {
        "total_datasets": len(datasets),
        "total_downloads": sum(d.get("downloads", 0) for d in datasets),
        "total_likes": sum(d.get("likes", 0) for d in datasets),
        "top_authors": {},
        "top_tasks": {},
        "multilingual_count": 0
    }

    # 저자별 통계
    for dataset in datasets:
        author = dataset.get("author", "unknown")
        stats["top_authors"][author] = stats["top_authors"].get(author, 0) + 1

        # 작업별 통계
        for task in dataset.get("tasks", []):
            stats["top_tasks"][task] = stats["top_tasks"].get(task, 0) + 1

        # 다국어 데이터셋 카운트
        if len(dataset.get("languages", [])) > 1:
            stats["multilingual_count"] += 1

    # 상위 10개만 유지
    stats["top_authors"] = dict(sorted(stats["top_authors"].items(),
                                       key=lambda x: x[1], reverse=True)[:10])
    stats["top_tasks"] = dict(sorted(stats["top_tasks"].items(),
                                     key=lambda x: x[1], reverse=True)[:10])

    return stats


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("한국어 데이터셋 수집 도구")
    print("=" * 60)

    # 데이터셋 수집
    datasets = collect_korean_datasets()

    if not datasets:
        print("수집된 데이터셋이 없습니다.")
        return

    # 데이터 저장
    output_file = process_and_save_datasets(datasets)

    # 통계 생성 및 저장
    stats = generate_statistics(datasets)
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d")

    stats_data = {
        "last_updated": current_time.isoformat(),
        "statistics": stats
    }

    # 현재 통계 저장
    stats_file = "docs/data/statistics.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)

    # 아카이브에도 통계 저장
    archive_stats_file = f"docs/data/archive/statistics_{timestamp}.json"
    with open(archive_stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)

    print(f"\n통계 정보:")
    print(f"  - 총 데이터셋: {stats['total_datasets']}")
    print(f"  - 총 다운로드: {stats['total_downloads']:,}")
    print(f"  - 총 좋아요: {stats['total_likes']:,}")
    print(f"  - 다국어 데이터셋: {stats['multilingual_count']}")
    print(f"\n통계 파일: {stats_file}")

    print("\n" + "=" * 60)
    print("수집 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
