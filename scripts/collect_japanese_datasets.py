#!/usr/bin/env python3
"""
Script to collect and organize Japanese language datasets from Hugging Face
"""
import json
import os
from datetime import datetime
from typing import List, Dict
import pandas as pd
from huggingface_hub import HfApi, list_datasets
from tqdm import tqdm


def collect_japanese_datasets() -> List[Dict]:
    """Collect datasets that include Japanese language from Hugging Face."""
    api = HfApi()
    datasets = []

    print("Collecting Japanese datasets...")

    # Search for datasets with Japanese language tag (ja)
    try:
        for dataset in tqdm(list_datasets(language="ja", full=True)):
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

                # Extract language, task, and size information from tags
                if dataset.tags:
                    for tag in dataset.tags:
                        if tag.startswith("language:"):
                            dataset_info["languages"].append(tag.replace("language:", ""))
                        elif tag.startswith("task_categories:"):
                            dataset_info["tasks"].append(tag.replace("task_categories:", ""))
                        elif tag.startswith("size_categories:"):
                            dataset_info["size_categories"].append(tag.replace("size_categories:", ""))

                # Filter: Include Japanese datasets with up to 100 languages
                if "ja" in dataset_info["languages"]:
                    # Japanese + max 100 languages
                    if len(dataset_info["languages"]) <= 100:
                        datasets.append(dataset_info)
            except Exception as e:
                print(f"Error processing dataset {dataset.id}: {e}")
                continue

    except Exception as e:
        print(f"Error fetching dataset list: {e}")

    return datasets


def process_and_save_datasets(datasets: List[Dict], output_dir: str = "docs/data"):
    """Process dataset information and save to JSON files."""
    os.makedirs(output_dir, exist_ok=True)
    archive_dir = os.path.join(output_dir, "archive")
    os.makedirs(archive_dir, exist_ok=True)

    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d")

    # Current data structure
    current_data = {
        "last_updated": current_time.isoformat(),
        "total_count": len(datasets),
        "datasets": datasets
    }

    # 1. Save current data to archive (by date)
    archive_file = os.path.join(archive_dir, f"japanese_datasets_{timestamp}.json")
    with open(archive_file, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, ensure_ascii=False, indent=2)
    print(f"Archive saved: {archive_file}")

    # 2. Save latest data to main file
    output_file = os.path.join(output_dir, "japanese_datasets.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved information for {len(datasets)} datasets.")
    print(f"File location: {output_file}")

    # 3. Also save as CSV (for backup)
    if datasets:
        df = pd.DataFrame(datasets)
        csv_file = os.path.join(output_dir, "japanese_datasets.csv")
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"CSV file: {csv_file}")

        # Archive CSV as well
        archive_csv = os.path.join(archive_dir, f"japanese_datasets_{timestamp}.csv")
        df.to_csv(archive_csv, index=False, encoding='utf-8-sig')

    return output_file


def generate_statistics(datasets: List[Dict]) -> Dict:
    """Generate statistics information for datasets."""
    stats = {
        "total_datasets": len(datasets),
        "total_downloads": sum(d.get("downloads", 0) for d in datasets),
        "total_likes": sum(d.get("likes", 0) for d in datasets),
        "top_authors": {},
        "top_tasks": {},
        "multilingual_count": 0
    }

    # Statistics by author
    for dataset in datasets:
        author = dataset.get("author", "unknown")
        stats["top_authors"][author] = stats["top_authors"].get(author, 0) + 1

        # Statistics by task
        for task in dataset.get("tasks", []):
            stats["top_tasks"][task] = stats["top_tasks"].get(task, 0) + 1

        # Count multilingual datasets
        if len(dataset.get("languages", [])) > 1:
            stats["multilingual_count"] += 1

    # Keep only top 10
    stats["top_authors"] = dict(sorted(stats["top_authors"].items(),
                                       key=lambda x: x[1], reverse=True)[:10])
    stats["top_tasks"] = dict(sorted(stats["top_tasks"].items(),
                                     key=lambda x: x[1], reverse=True)[:10])

    return stats


def main():
    """Main execution function"""
    print("=" * 60)
    print("Japanese Dataset Collection Tool")
    print("=" * 60)

    # Collect datasets
    datasets = collect_japanese_datasets()

    if not datasets:
        print("No datasets collected.")
        return

    # Save data
    output_file = process_and_save_datasets(datasets)

    # Generate and save statistics
    stats = generate_statistics(datasets)
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d")

    stats_data = {
        "last_updated": current_time.isoformat(),
        "statistics": stats
    }

    # Save current statistics
    stats_file = "docs/data/statistics.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)

    # Save statistics to archive as well
    archive_stats_file = f"docs/data/archive/statistics_{timestamp}.json"
    with open(archive_stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)

    print(f"\nStatistics:")
    print(f"  - Total datasets: {stats['total_datasets']}")
    print(f"  - Total downloads: {stats['total_downloads']:,}")
    print(f"  - Total likes: {stats['total_likes']:,}")
    print(f"  - Multilingual datasets: {stats['multilingual_count']}")
    print(f"\nStatistics file: {stats_file}")

    print("\n" + "=" * 60)
    print("Collection complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
