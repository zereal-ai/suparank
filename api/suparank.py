from pyairtable import Table
from typing import List, Dict, Optional, Tuple
import math
import time

class Suparank:
    def __init__(self, token: str):
        self.entries: List[Dict] = []
        self.token = token
        self.table = None
        self.compared_pairs = set()
        self.current_level = 0
        self.total_levels = 0
        self.debug_output = []

    def set_base(self, base_id: str, table_id: str = "tblDb3jQiPGFeDU9e") -> None:
        self.table = Table(self.token, base_id, table_id)
        self.load_entries()
        self._init_merge_sort()

    def load_entries(self) -> None:
        """Load entries from Airtable with detailed debug logging"""
        self.debug_output = []  # Clear previous debug output
        self.debug_output.append("\n=== Loading entries from Airtable ===")
        
        # Add cache-busting timestamp to force fresh data
        timestamp = int(time.time() * 1000)
        self.debug_output.append(f"\nFetching records at timestamp: {timestamp}")
        
        # Use a simple formula that's always true to ensure we get all records
        records = self.table.all(formula="OR(1, 0)")
        
        self.debug_output.append(f"\nReceived {len(records)} records from Airtable")
        
        self.debug_output.append("\nRaw Airtable records:")
        for record in records:
            fields_str = ", ".join(f"{k}: {v}" for k, v in record['fields'].items())
            self.debug_output.append(f"ID: {record['id']}, Fields: {fields_str}")
            
        # Clear the entries list before repopulating
        self.entries = []
        
        # Populate entries from records
        self.entries = [
            {
                "id": record["id"],
                "title": record["fields"].get("Title", "Untitled"),
                "description": record["fields"].get("Description", ""),
                "rank": record["fields"].get("Rank"),  # Rank can be None (unranked) or int
            }
            for record in records
        ]
        
        self.debug_output.append("\nProcessed entries:")
        for entry in self.entries:
            self.debug_output.append(f"ID: {entry['id']}, Title: {entry['title']}, Rank: {entry['rank']}")
        
        self.debug_output.append("\n=== Finished loading entries ===\n")

    def _init_merge_sort(self) -> None:
        """Initialize merge sort parameters"""
        n = len(self.entries)
        if n < 2:
            return
        
        self.total_levels = math.ceil(math.log2(n))
        self.current_level = 0
        self.compared_pairs.clear()
        self.debug_output = []
        self.debug_output.append(f"Initialized merge sort: {n} items, {self.total_levels} levels needed")

    def _has_unranked_items(self) -> bool:
        """Check if there are any unranked items"""
        return any(entry["rank"] is None for entry in self.entries)

    def get_next_pair(self) -> Optional[Tuple[Dict, Dict]]:
        """Get next pair to compare based on merge sort level"""
        self.debug_output = []
        
        if len(self.entries) < 2:
            self.debug_output.append("Not enough entries for comparison")
            return None

        # If we've completed all levels but still have unranked items, reset level
        if self.current_level >= self.total_levels:
            if self._has_unranked_items():
                self.debug_output.append("Resetting to level 0 to handle remaining unranked items")
                self.compared_pairs.clear()
                self.current_level = 0
            else:
                self.debug_output.append("All items have been ranked!")
                return None

        n = len(self.entries)
        group_size = 2 ** self.current_level

        self.debug_output.append(f"\nLevel {self.current_level}/{self.total_levels-1}, Group size: {group_size}")
        
        # Iterate through groups at current level
        for group_start in range(0, n, group_size * 2):
            left_start = group_start
            mid = min(group_start + group_size, n)
            right_start = mid
            right_end = min(group_start + group_size * 2, n)

            self.debug_output.append(f"Group: {group_start}-{right_end}, Split at: {mid}")
            
            # Compare elements from left and right halves
            left = left_start
            right = right_start
            
            while left < mid and right < right_end:
                pair = (min(left, right), max(left, right))
                if pair not in self.compared_pairs:
                    self.debug_output.append(f"Found pair to compare: {self.entries[left]['title']} vs {self.entries[right]['title']}")
                    return self.entries[left], self.entries[right]
                left += 1
                right += 1

        self.current_level += 1
        self.debug_output.append(f"Moving to level {self.current_level}")
        return self.get_next_pair()

    def choose_winner(self, winner_id: str, loser_id: str) -> None:
        """Update ranks when a winner is chosen"""
        self.debug_output = []
        winner = next(entry for entry in self.entries if entry["id"] == winner_id)
        loser = next(entry for entry in self.entries if entry["id"] == loser_id)
        
        self.debug_output.append(f"\nProcessing winner choice:")
        self.debug_output.append(f"Winner: {winner['title']} (current rank: {winner['rank']})")
        self.debug_output.append(f"Loser: {loser['title']} (current rank: {loser['rank']})")
        
        # Mark this pair as compared
        winner_idx = self.entries.index(winner)
        loser_idx = self.entries.index(loser)
        self.compared_pairs.add((min(winner_idx, loser_idx), max(winner_idx, loser_idx)))

        # Get all entries sorted by current rank (None last)
        sorted_entries = sorted(
            self.entries,
            key=lambda x: (x["rank"] is None, x["rank"] if x["rank"] is not None else float('inf'))
        )

        if winner["rank"] is None and loser["rank"] is None:
            # Both unranked: winner gets rank 1, loser gets rank 2
            self.debug_output.append("Both items unranked, assigning initial ranks")
            winner["rank"] = 1
            loser["rank"] = 2
        elif winner["rank"] is None:
            # Winner unranked: insert before loser
            loser_rank = loser["rank"]
            if loser_rank is not None:  # Safety check
                self.debug_output.append(f"Winner unranked, inserting at rank {loser_rank}")
                for entry in sorted_entries:
                    if entry["rank"] is not None and entry["rank"] >= loser_rank:
                        entry["rank"] += 1
                        self.table.update(entry["id"], {"Rank": entry["rank"]})
                winner["rank"] = loser_rank
        elif loser["rank"] is None:
            # Loser unranked: insert after winner
            winner_rank = winner["rank"]
            if winner_rank is not None:  # Safety check
                self.debug_output.append(f"Loser unranked, inserting at rank {winner_rank + 1}")
                loser["rank"] = winner_rank + 1
                for entry in sorted_entries:
                    if entry["rank"] is not None and entry["rank"] > winner_rank:
                        entry["rank"] += 1
                        self.table.update(entry["id"], {"Rank": entry["rank"]})
        else:
            # Both ranked: if winner's rank > loser's rank, swap them
            if winner["rank"] > loser["rank"]:
                self.debug_output.append(f"Swapping ranks: winner {winner['rank']} -> {loser['rank']}, loser {loser['rank']} -> {winner['rank']}")
                old_winner_rank = winner["rank"]
                old_loser_rank = loser["rank"]
                winner["rank"] = old_loser_rank
                
                # Shift all ranks between loser and winner up by 1
                for entry in sorted_entries:
                    if entry["id"] not in [winner_id, loser_id]:
                        if entry["rank"] is not None and old_loser_rank <= entry["rank"] < old_winner_rank:
                            entry["rank"] += 1
                            self.table.update(entry["id"], {"Rank": entry["rank"]})
                
                loser["rank"] = old_winner_rank

        # Ensure ranks are consecutive integers starting from 1
        ranked_entries = [e for e in sorted_entries if e["rank"] is not None]
        ranked_entries.sort(key=lambda x: x["rank"] if x["rank"] is not None else float('inf'))
        
        self.debug_output.append("\nFinalizing ranks:")
        for i, entry in enumerate(ranked_entries, 1):
            if entry["rank"] != i:
                old_rank = entry["rank"]
                entry["rank"] = i
                self.table.update(entry["id"], {"Rank": i})
                self.debug_output.append(f"Adjusted {entry['title']}: {old_rank} -> {i}")

        # Update the winner and loser in Airtable
        self.table.update(winner["id"], {"Rank": winner["rank"]})
        self.table.update(loser["id"], {"Rank": loser["rank"]})
        
        self.debug_output.append(f"\nFinal result:")
        self.debug_output.append(f"Winner {winner['title']} (rank: {winner['rank']})")
        self.debug_output.append(f"Loser {loser['title']} (rank: {loser['rank']})")

    def get_rankings(self) -> List[Dict]:
        """Get current rankings sorted by rank (None last)"""
        self.debug_output = []
        
        # Sort entries: ranked items first (by rank), then unranked
        rankings = sorted(
            self.entries,
            key=lambda x: (x["rank"] is None, x["rank"] if x["rank"] is not None else float('inf'))
        )
        
        self.debug_output.append("\nCurrent Rankings:")
        for i, r in enumerate(rankings):
            rank_str = str(r["rank"]) if r["rank"] is not None else "unranked"
            self.debug_output.append(f"{i+1}. {r['title']} (rank: {rank_str})")
        
        if self._has_unranked_items():
            self.debug_output.append("\nWARNING: Some items are still unranked")
        
        return rankings

    def add_entry(self, title: str, description: str) -> Dict:
        """Add a new unranked entry"""
        record = self.table.create(
            {"Title": title, "Description": description}  # No rank field = NULL in Airtable
        )

        entry = {
            "id": record["id"],
            "title": title,
            "description": description,
            "rank": None,
        }
        self.entries.append(entry)
        self._init_merge_sort()
        return entry

    def get_debug_info(self) -> List[str]:
        """Get debug information about the merge sort process"""
        return self.debug_output

    def reset_ranking(self) -> None:
        """Reset all ranks to None and reinitialize merge sort"""
        self.debug_output = []
        self.debug_output.append("Starting rank reset...")
        
        # First load fresh data to ensure we have all records
        self.load_entries()
        
        if len(self.entries) < 2:
            raise ValueError("Need at least 2 entries to start ranking")
        
        # Prepare records for batch update
        records = [
            {
                "id": entry["id"],
                "fields": {
                    "Rank": None
                }
            }
            for entry in self.entries
        ]
        
        try:
            # Update records in chunks of 10 (Airtable's limit)
            CHUNK_SIZE = 10
            for i in range(0, len(records), CHUNK_SIZE):
                chunk = records[i:i + CHUNK_SIZE]
                self.debug_output.append(f"Batch updating records {i+1} to {i+len(chunk)}")
                self.table.batch_update(chunk)
                # Small delay between chunks to avoid rate limiting
                if i + CHUNK_SIZE < len(records):
                    time.sleep(0.2)
            
            # Clear ranks in local state
            for entry in self.entries:
                entry["rank"] = None
                
            self.debug_output.append("Successfully cleared all ranks")
        except Exception as e:
            self.debug_output.append(f"Error in batch update: {str(e)}")
            raise ValueError(f"Failed to clear ranks: {str(e)}")
        
        # Force a delay to ensure Airtable updates are processed
        time.sleep(1)
        
        # Reload entries to verify changes
        self.load_entries()
        
        # Verify all ranks are None
        any_ranked = any(entry["rank"] is not None for entry in self.entries)
        if any_ranked:
            self.debug_output.append("WARNING: Some entries still have ranks after reset!")
            for entry in self.entries:
                if entry["rank"] is not None:
                    self.debug_output.append(f"Entry still ranked: {entry['title']} (rank: {entry['rank']})")
            raise ValueError("Failed to reset all ranks")
        
        self.debug_output.append("Verified all entries are unranked")
        
        # Reset merge sort state
        self.current_level = 0
        self.compared_pairs.clear()
        self.total_levels = math.ceil(math.log2(len(self.entries)))
        
        self.debug_output.append("Rankings reset complete") 