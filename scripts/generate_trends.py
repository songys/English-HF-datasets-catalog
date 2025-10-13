#!/usr/bin/env python3
"""
아카이브된 데이터로부터 트렌드 데이터를 생성하는 스크립트
"""
import json
import os
from datetime import datetime
from typing import List, Dict
import glob


def load_archived_statistics() -> List[Dict]:
    """아카이브된 통계 파일들을 로드합니다."""
    archive_dir = "docs/data/archive"
    stats_files = sorted(glob.glob(os.path.join(archive_dir, "statistics_*.json")))

    all_stats = []
    for file_path in stats_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 파일명에서 날짜 추출
            filename = os.path.basename(file_path)
            date_str = filename.replace("statistics_", "").replace(".json", "")

            all_stats.append({
                "date": date_str,
                "last_updated": data.get("last_updated"),
                "statistics": data.get("statistics", {})
            })

    return all_stats


def generate_trend_data(all_stats: List[Dict]) -> Dict:
    """트렌드 데이터를 생성합니다."""
    if not all_stats:
        return {
            "dates": [],
            "total_datasets": [],
            "total_downloads": [],
            "total_likes": [],
            "multilingual_count": [],
            "growth_rate": 0,
            "latest_stats": {}
        }

    dates = []
    total_datasets = []
    total_downloads = []
    total_likes = []
    multilingual_count = []

    for entry in all_stats:
        stats = entry["statistics"]
        dates.append(entry["date"])
        total_datasets.append(stats.get("total_datasets", 0))
        total_downloads.append(stats.get("total_downloads", 0))
        total_likes.append(stats.get("total_likes", 0))
        multilingual_count.append(stats.get("multilingual_count", 0))

    # 성장률 계산
    growth_rate = 0
    if len(total_datasets) >= 2 and total_datasets[0] > 0:
        growth_rate = ((total_datasets[-1] - total_datasets[0]) / total_datasets[0]) * 100

    return {
        "dates": dates,
        "total_datasets": total_datasets,
        "total_downloads": total_downloads,
        "total_likes": total_likes,
        "multilingual_count": multilingual_count,
        "growth_rate": round(growth_rate, 2),
        "latest_stats": all_stats[-1]["statistics"] if all_stats else {},
        "first_date": dates[0] if dates else None,
        "last_date": dates[-1] if dates else None,
        "total_weeks": len(dates)
    }


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("트렌드 데이터 생성 도구")
    print("=" * 60)

    # 아카이브된 통계 로드
    all_stats = load_archived_statistics()

    if not all_stats:
        print("아카이브된 통계 데이터가 없습니다.")
        return

    print(f"총 {len(all_stats)}개의 아카이브 파일 발견")

    # 트렌드 데이터 생성
    trend_data = generate_trend_data(all_stats)

    # 트렌드 데이터 저장
    output_file = "docs/data/trends.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "trends": trend_data
        }, f, ensure_ascii=False, indent=2)

    print(f"\n트렌드 데이터 저장: {output_file}")
    print(f"  - 기간: {trend_data['first_date']} ~ {trend_data['last_date']}")
    print(f"  - 총 주차: {trend_data['total_weeks']}")
    print(f"  - 성장률: {trend_data['growth_rate']}%")

    print("\n" + "=" * 60)
    print("생성 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
