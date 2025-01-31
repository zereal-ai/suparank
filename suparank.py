import os
from rich.console import Console
from rich.panel import Panel
from rich import box
from pyairtable import Api


class Suparank:
    def __init__(self, token):
        self.entries = []
        self.current_pair_index = 0
        self.console = Console()

        # Airtable setup
        self.api = Api(token)
        self.table = None

        # Merge sort state
        self.current_level = 0
        self.compared_pairs = set()

    def set_base(self, base_id, table_id="tblDb3jQiPGFeDU9e"):
        self.table = self.api.table(base_id, table_id)
        self.load_entries()

    def load_entries(self):
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
        self.pairs = self._generate_merge_pairs()

    def _generate_merge_pairs(self):
        """Generate pairs following merge sort pattern"""
        n = len(self.entries)
        if n < 2:
            return []

        # Calculate total levels needed for merge sort
        self.total_levels = 0
        size = 1
        while size < n:
            size *= 2
            self.total_levels += 1

        # Start with base level pairs
        pairs = []
        for i in range(0, n - 1, 2):
            if i + 1 < n:
                pairs.append((i, i + 1))

        return pairs

    def _get_next_merge_pair(self):
        """Get next pair to compare based on merge sort level"""
        n = len(self.entries)
        if n < 2:
            return None

        size = 2**self.current_level
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
                    return pair
                left += 1
                right += 1

        # Move to next level if current level is complete
        self.current_level += 1
        if self.current_level < self.total_levels:
            return self._get_next_merge_pair()

        return None

    def add_entry(self, title, description):
        # Create new record in Airtable
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

    def display_current_pair(self):
        os.system("clear")

        pair = self._get_next_merge_pair()
        if not pair:
            self.console.print("\n[yellow]Ranking complete![/yellow]")
            return False

        left_idx, right_idx = pair
        left_entry = self.entries[left_idx]
        right_entry = self.entries[right_idx]

        self.console.print("\n" * 2)
        self.console.print(
            Panel(
                f"[bold blue]Which entry is more important?[/bold blue]\n\n"
                + f"[bold green]LEFT:[/bold green] {left_entry['title']}\n{left_entry['description']}\n\n"
                + f"[bold red]RIGHT:[/bold red] {right_entry['title']}\n{right_entry['description']}",
                title=f"Suparank - Level {self.current_level + 1}/{self.total_levels}",
                subtitle="← (Left is more important) | (Right is more important) →",
                box=box.ROUNDED,
                padding=(1, 2),
                width=80,
            )
        )
        return True

    def choose_left(self):
        pair = self._get_next_merge_pair()
        if pair:
            left_idx, right_idx = pair
            left_entry = self.entries[left_idx]
            right_entry = self.entries[right_idx]

            # Update scores
            new_score = right_entry["score"] + 1
            left_entry["score"] = new_score
            self.table.update(left_entry["id"], {"Score": new_score})

            # Mark this pair as compared
            self.compared_pairs.add(pair)

    def choose_right(self):
        pair = self._get_next_merge_pair()
        if pair:
            left_idx, right_idx = pair
            left_entry = self.entries[left_idx]
            right_entry = self.entries[right_idx]

            # Update scores
            new_score = left_entry["score"] + 1
            right_entry["score"] = new_score
            self.table.update(right_entry["id"], {"Score": new_score})

            # Mark this pair as compared
            self.compared_pairs.add(pair)

    def show_final_ranking(self):
        self.console.print("\n[bold]Final Rankings:[/bold]")
        # Query Airtable for entries sorted by score in descending order
        sorted_entries = self.table.all(sort=["-Score"])

        for i, entry in enumerate(sorted_entries, 1):
            fields = entry["fields"]
            self.console.print(
                f"\n{i}. [bold]{fields['Title']}[/bold] (Score: {fields['Score']})"
            )
            self.console.print(f"   {fields['Description']}")
