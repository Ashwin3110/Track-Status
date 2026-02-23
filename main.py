import asyncio
import sys
from config.config_loader import load_providers
from core.state_manager import StateManager
from core.scheduler import Scheduler
from notifiers.console_notifier import ConsoleNotifier


async def main():
    print("=" * 60)
    print("   STATUS PAGE TRACKER")
    print("   Monitoring for incidents across all providers")
    print("=" * 60 + "\n")

    # Step 1 — Load providers from config
    try:
        providers = load_providers()
    except Exception as e:
        print(f"[Main] Failed to load config: {e}")
        sys.exit(1)

    # Step 2 — Initialize and load state manager
    state_manager = StateManager()
    await state_manager.load()

    # Step 3 — Set up notifiers
    # Add more notifiers to this list later e.g. SlackNotifier()
    notifiers = [
        ConsoleNotifier()
    ]

    # Step 4 — Create the scheduler
    scheduler = Scheduler(
        providers=providers,
        state_manager=state_manager,
        notifiers=notifiers
    )

    # Step 5 — Run forever, handle Ctrl+C gracefully
    try:
        await scheduler.run()
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        print("\n[Main] Shutting down. Saving final state...")
        await state_manager.save()
        print("[Main] State saved. Goodbye.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass