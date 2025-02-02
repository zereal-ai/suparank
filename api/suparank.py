from pyairtable import Api
from typing import List, Dict, Optional, Tuple
import math
from datetime import datetime


class Suparank:
    def __init__(self, token: str):
        self.token = token
        self.api = Api(token)
        self.items_table = None
        self.splits_table = None
        self.merges_table = None
        self.items = []

    def set_base(self, base_id: str) -> None:
        """Initialize tables and load items"""
        # Get table IDs from base
        response = self.api.get(
            f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
        )
        tables = {t["name"]: t["id"] for t in response["tables"]}
        
        # Initialize table connections
        self.items_table = self.api.table(base_id, tables["Items"])
        self.splits_table = self.api.table(base_id, tables["Splits"])
        self.merges_table = self.api.table(base_id, tables["Merges"])
        
        # Load items
        self.load_items()

    def load_items(self) -> None:
        """Load items from Airtable"""
        records = self.items_table.all()
        self.items = [
            {
                "id": record["id"],
                "title": record["fields"].get("Title", "Untitled"),
                "description": record["fields"].get("Description", "")
            }
            for record in records
        ]
        
        # Check if we need to initialize a ranking session
        splits = self.splits_table.all()
        if not splits and len(self.items) >= 2:
            self._init_merge_sort()

    def _init_merge_sort(self) -> None:
        """Start a new merge sort session"""
        if len(self.items) < 2:
            return

        # Clear existing splits and merges
        for record in self.splits_table.all():
            self.splits_table.delete(record["id"])
        for record in self.merges_table.all():
            self.merges_table.delete(record["id"])

        # Create initial splits at level 0
        for i, item in enumerate(self.items):
            self.splits_table.create({
                "ItemID": item["id"],
                "SplitID": i,
                "SplitLevel": 0,
                "Side": "left" if i % 2 == 0 else "right",
                "ParentSplitID": i // 2
            })

    def get_next_pair(self) -> Optional[Tuple[Dict, Dict]]:
        """Get next pair of items to compare"""
        if len(self.items) < 2:
            return None

        # Find lowest level with unmerged pairs
        splits = self.splits_table.all()
        if not splits:
            # Initialize merge sort if not already done
            self._init_merge_sort()
            splits = self.splits_table.all()
            if not splits:  # If still no splits, we can't proceed
                return None

        # Group splits by level
        splits_by_level = {}
        for split in splits:
            level = split["fields"]["SplitLevel"]
            splits_by_level.setdefault(level, []).append(split)

        if not splits_by_level:
            return None

        min_level = min(splits_by_level.keys())
        level_splits = splits_by_level[min_level]

        # Find adjacent pairs at this level
        for i in range(0, len(level_splits), 2):
            if i + 1 >= len(level_splits):
                continue

            left_split = level_splits[i]
            right_split = level_splits[i + 1]

            # Check if this pair has been compared
            existing_merge = self.merges_table.all(
                formula=f"AND(SplitID={left_split['fields']['SplitID']}, SplitLevel={min_level})"
            )
            if existing_merge:
                continue

            # Get the actual items
            left_item = next(item for item in self.items if item["id"] == left_split["fields"]["ItemID"])
            right_item = next(item for item in self.items if item["id"] == right_split["fields"]["ItemID"])

            return left_item, right_item

        # If no pairs found at this level, promote completed pairs to next level
        self._promote_level(min_level)
        return self.get_next_pair()

    def _promote_level(self, level: int) -> None:
        """Promote merged pairs to next level"""
        # Get all merges at this level
        merges = self.merges_table.all(
            formula=f"SplitLevel={level}"
        )

        # Group merges by parent split
        merges_by_parent = {}
        for merge in merges:
            parent_id = merge["fields"]["SplitID"]
            merges_by_parent.setdefault(parent_id, []).append(merge)

        # Create new splits at next level
        new_split_id = 0
        for parent_id, parent_merges in merges_by_parent.items():
            # Sort merges by position
            parent_merges.sort(key=lambda m: m["fields"]["Position"])
            
            # Create new splits for merged items
            for i, merge in enumerate(parent_merges):
                self.splits_table.create({
                    "ItemID": merge["fields"]["WinnerID"],
                    "SplitID": new_split_id,
                    "SplitLevel": level + 1,
                    "Side": "left" if i % 2 == 0 else "right",
                    "ParentSplitID": new_split_id // 2
                })
            new_split_id += 1

    def choose_winner(self, winner_id: str, loser_id: str) -> None:
        """Record user's choice between two items"""
        # Find the splits for these items
        winner_split = next(
            split for split in self.splits_table.all()
            if split["fields"]["ItemID"] == winner_id
        )
        loser_split = next(
            split for split in self.splits_table.all()
            if split["fields"]["ItemID"] == loser_id
        )

        # Record the merge
        split_level = winner_split["fields"]["SplitLevel"]
        split_id = winner_split["fields"]["ParentSplitID"]

        # Get position for this merge
        existing_merges = self.merges_table.all(
            formula=f"AND(SplitID={split_id}, SplitLevel={split_level})"
        )
        position = len(existing_merges)

        # Create merge record
        self.merges_table.create({
            "MergeID": len(existing_merges),
            "SplitID": split_id,
            "SplitLevel": split_level,
            "Position": position,
            "WinnerID": winner_id,
            "LoserID": loser_id,
            "CompareTime": datetime.now().isoformat()
        })

        # Delete the splits that were merged
        self.splits_table.delete(winner_split["id"])
        self.splits_table.delete(loser_split["id"])

    def get_rankings(self) -> List[Dict]:
        """Get current rankings based on merge history"""
        # Get all merges
        merges = self.merges_table.all()
        if not merges:
            return self.items

        # Build ranking from merge history
        rankings = []
        seen_items = set()

        # Process merges in chronological order
        sorted_merges = sorted(merges, key=lambda m: m["fields"]["CompareTime"])
        
        for merge in sorted_merges:
            winner_id = merge["fields"]["WinnerID"]
            loser_id = merge["fields"]["LoserID"]

            # Add winner if not seen
            if winner_id not in seen_items:
                winner = next(item for item in self.items if item["id"] == winner_id)
                rankings.append(winner)
                seen_items.add(winner_id)

            # Add loser if not seen
            if loser_id not in seen_items:
                loser = next(item for item in self.items if item["id"] == loser_id)
                rankings.append(loser)
                seen_items.add(loser_id)

        # Add any remaining items
        for item in self.items:
            if item["id"] not in seen_items:
                rankings.append(item)

        # Calculate ranks based on final position
        # Only assign ranks if all items have been compared
        if len(rankings) == len(self.items):
            for i, item in enumerate(rankings, start=1):
                item["rank"] = i

        return rankings

    def reset_ranking(self) -> None:
        """Start a new ranking session"""
        self._init_merge_sort()

    def add_item(self, title: str, description: str) -> Dict:
        """Add a new item"""
        record = self.items_table.create({
            "Title": title,
            "Description": description
        })
        
        item = {
            "id": record["id"],
            "title": title,
            "description": description
        }
        self.items.append(item)
        return item
