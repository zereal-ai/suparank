from pyairtable import Table
from typing import List, Dict, Optional, Tuple

class Suparank:
    def __init__(self, token: str):
        self.entries: List[Dict] = []
        self.token = token
        self.table = None
        self.current_level = 0
        self.compared_pairs = set()
        self.total_levels = 0

    def set_base(self, base_id: str, table_id: str = "Items") -> None:
        self.table = Table(self.token, base_id, table_id)
        self.load_entries()

    def load_entries(self) -> None:
        records = self.table.all()
        self.entries = [
            {
                "id": record["id"],
                "title": record["fields"].get("Title", "Untitled"),
                "description": record["fields"].get("Description", ""),
                "score": float(record["fields"].get("Score", "0")),
            }
            for record in records
        ]
        self._generate_merge_pairs()

    def _generate_merge_pairs(self) -> None:
        n = len(self.entries)
        if n < 2:
            return

        # Calculate total levels needed for merge sort
        self.total_levels = 0
        size = 1
        while size < n:
            size *= 2
            self.total_levels += 1

    def get_next_pair(self) -> Optional[Tuple[Dict, Dict]]:
        """Get next pair to compare based on merge sort level"""
        n = len(self.entries)
        if n < 2:
            return None

        size = 2 ** self.current_level
        for i in range(0, n, size * 2):
            left_start = i
            mid = min(i + size, n)
            right_start = mid
            right_end = min(i + size * 2, n)

            # Compare elements from left and right halves
            left = left_start
            right = right_start

            while left < mid and right < right_end:
                pair = (left, right)
                if pair not in self.compared_pairs:
                    return self.entries[left], self.entries[right]
                left += 1
                right += 1

        # Move to next level if current level is complete
        self.current_level += 1
        if self.current_level < self.total_levels:
            return self.get_next_pair()

        return None

    def choose_winner(self, winner_id: str, loser_id: str) -> None:
        """Update scores when a winner is chosen"""
        winner = next(entry for entry in self.entries if entry["id"] == winner_id)
        loser = next(entry for entry in self.entries if entry["id"] == loser_id)
        
        # Find indices to mark as compared
        winner_idx = self.entries.index(winner)
        loser_idx = self.entries.index(loser)
        self.compared_pairs.add((min(winner_idx, loser_idx), max(winner_idx, loser_idx)))

        # Update winner's score
        new_score = loser["score"] + 1
        winner["score"] = new_score
        self.table.update(winner["id"], {"Score": new_score})

    def get_rankings(self) -> List[Dict]:
        """Get current rankings sorted by score"""
        return sorted(self.entries, key=lambda x: x["score"], reverse=True)

    def add_entry(self, title: str, description: str) -> Dict:
        """Add a new entry to be ranked"""
        record = self.table.create(
            {"Title": title, "Description": description, "Score": 0}
        )

        entry = {
            "id": record["id"],
            "title": title,
            "description": description,
            "score": 0,
        }
        self.entries.append(entry)
        self._generate_merge_pairs()  # Regenerate pairs with new entry
        return entry 