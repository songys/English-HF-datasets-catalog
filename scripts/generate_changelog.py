#!/usr/bin/env python3
"""
Script to analyze weekly dataset changes and generate changelog
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Set


def load_dataset(file_path: str) -> Dict:
    """JSON 파일에서 데이터셋을 로드합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def get_latest_two_archives() -> tuple:
    """가장 최근 2개의 아카이브 파일을 반환합니다."""
    archive_dir = "docs/data/archive"
    files = sorted([f for f in os.listdir(archive_dir) if f.startswith("english_datasets_") and f.endswith(".json")])

    if len(files) < 2:
        return None, None

    previous_file = os.path.join(archive_dir, files[-2])
    current_file = os.path.join(archive_dir, files[-1])

    return previous_file, current_file


def compare_datasets(previous_data: Dict, current_data: Dict) -> Dict:
    """두 데이터셋을 비교하여 변경사항을 찾습니다."""
    if not previous_data or not current_data:
        return {
            "new_datasets": [],
            "removed_datasets": [],
            "updated_datasets": [],
            "unchanged_count": 0
        }

    # 데이터셋 ID를 딕셔너리로 변환
    previous_dict = {ds["id"]: ds for ds in previous_data["datasets"]}
    current_dict = {ds["id"]: ds for ds in current_data["datasets"]}

    previous_ids = set(previous_dict.keys())
    current_ids = set(current_dict.keys())

    # 새로 추가된 데이터셋
    new_ids = current_ids - previous_ids
    new_datasets = [current_dict[id] for id in new_ids]

    # 삭제된 데이터셋
    removed_ids = previous_ids - current_ids
    removed_datasets = [previous_dict[id] for id in removed_ids]

    # 변경된 데이터셋 (다운로드, 좋아요 등)
    common_ids = previous_ids & current_ids
    updated_datasets = []

    for id in common_ids:
        prev = previous_dict[id]
        curr = current_dict[id]

        # 다운로드, 좋아요, 설명이 변경되었는지 확인
        if (prev["downloads"] != curr["downloads"] or
            prev["likes"] != curr["likes"] or
            prev["description"] != curr["description"]):

            updated_datasets.append({
                "id": id,
                "author": curr["author"],
                "url": curr["url"],
                "changes": {
                    "downloads": {
                        "previous": prev["downloads"],
                        "current": curr["downloads"],
                        "change": curr["downloads"] - prev["downloads"]
                    },
                    "likes": {
                        "previous": prev["likes"],
                        "current": curr["likes"],
                        "change": curr["likes"] - prev["likes"]
                    },
                    "description_changed": prev["description"] != curr["description"]
                }
            })

    # 다운로드 증가량 기준으로 정렬
    updated_datasets.sort(key=lambda x: x["changes"]["downloads"]["change"], reverse=True)

    return {
        "new_datasets": new_datasets,
        "removed_datasets": removed_datasets,
        "updated_datasets": updated_datasets[:50],  # 상위 50개만
        "unchanged_count": len(common_ids) - len(updated_datasets)
    }


def generate_changelog() -> Dict:
    """변경사항을 생성하고 반환합니다."""
    previous_file, current_file = get_latest_two_archives()

    if not previous_file or not current_file:
        print("Not enough archive files to compare")
        return None

    print(f"Comparing:")
    print(f"  Previous: {previous_file}")
    print(f"  Current: {current_file}")

    previous_data = load_dataset(previous_file)
    current_data = load_dataset(current_file)

    if not previous_data or not current_data:
        print("Failed to load data files")
        return None

    changes = compare_datasets(previous_data, current_data)

    # 날짜 정보 추출
    previous_date = os.path.basename(previous_file).replace("english_datasets_", "").replace(".json", "")
    current_date = os.path.basename(current_file).replace("english_datasets_", "").replace(".json", "")

    changelog = {
        "generated_at": datetime.now().isoformat(),
        "previous_date": previous_date,
        "current_date": current_date,
        "previous_count": previous_data["total_count"],
        "current_count": current_data["total_count"],
        "changes": changes,
        "summary": {
            "new_count": len(changes["new_datasets"]),
            "removed_count": len(changes["removed_datasets"]),
            "updated_count": len(changes["updated_datasets"]),
            "unchanged_count": changes["unchanged_count"],
            "net_change": len(changes["new_datasets"]) - len(changes["removed_datasets"])
        }
    }

    return changelog


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("Weekly Changelog Generator")
    print("=" * 60)

    changelog = generate_changelog()

    if not changelog:
        print("No changelog generated")
        return

    # changelog 저장
    output_file = "docs/data/changelog.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(changelog, f, ensure_ascii=False, indent=2)

    print(f"\nChangelog saved: {output_file}")
    print(f"\nSummary:")
    print(f"  Period: {changelog['previous_date']} → {changelog['current_date']}")
    print(f"  New datasets: {changelog['summary']['new_count']}")
    print(f"  Removed datasets: {changelog['summary']['removed_count']}")
    print(f"  Updated datasets: {changelog['summary']['updated_count']}")
    print(f"  Unchanged datasets: {changelog['summary']['unchanged_count']}")
    print(f"  Net change: {changelog['summary']['net_change']:+d}")

    print("\n" + "=" * 60)
    print("Changelog generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
