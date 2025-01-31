from suparank import Suparank
from rich.console import Console
import keyboard
import os
import time
import signal
from dotenv import load_dotenv


def signal_handler(sig, frame):
    print("\n\nExiting gracefully...")
    exit(0)


def main():
    # Set up signal handler for CTRL+C
    signal.signal(signal.SIGINT, signal_handler)

    load_dotenv()

    token = os.getenv("AIRTABLE_TOKEN")
    base_id = os.getenv("AIRTABLE_BASE_ID")

    if not token or not base_id:
        print("Error: Please set AIRTABLE_TOKEN and AIRTABLE_BASE_ID in .env file")
        return

    app = Suparank(token)
    app.set_base(base_id)
    console = Console()

    console.print("[bold green]Welcome to Suparank![/bold green]")
    console.print("Compare entries and choose which is more important!")
    console.print("Press 'v' to view current rankings, CTRL+C to exit")
    time.sleep(2)

    try:
        while True:
            if not app.display_current_pair():
                console.print("\n[bold green]All entries have been ranked![/bold green]")
                app.show_final_ranking()
                break

            event = keyboard.read_event(suppress=True)
            if event.event_type == "down":
                if event.name == "left":
                    app.choose_left()
                    console.print("[green]Left entry ranked higher! ↑[/green]")
                    time.sleep(0.5)
                elif event.name == "right":
                    app.choose_right()
                    console.print("[red]Right entry ranked higher! ↑[/red]")
                    time.sleep(0.5)
                elif event.name == "v":
                    # Show current rankings
                    app.show_final_ranking()
                    input("\nPress Enter to continue...")
                elif event.name == "esc":
                    if (
                        input("\nShow final rankings before exiting? (y/n): ").lower()
                        == "y"
                    ):
                        app.show_final_ranking()
                    break

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted! Showing current rankings:[/yellow]")
        app.show_final_ranking()


if __name__ == "__main__":
    main()
