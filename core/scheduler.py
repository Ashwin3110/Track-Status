import asyncio
from typing import List

from config.config_loader import ProviderConfig
from adapters.atom_adapter import AtomAdapter
from core.change_detector import ChangeDetector
from core.state_manager import StateManager
from notifiers.base import BaseNotifier


class Scheduler:
    def __init__(
        self,
        providers: List[ProviderConfig],
        state_manager: StateManager,
        notifiers: List[BaseNotifier]
    ):
        self.providers = providers
        self.state_manager = state_manager
        self.notifiers = notifiers
        self.detector = ChangeDetector(state_manager)

    async def run(self):
        """
        Entry point. Launches one polling loop per provider,
        all running concurrently via asyncio.
        """
        print(f"[Scheduler] Starting monitoring for {len(self.providers)} provider(s)...")

        # Create one async task per provider, each running its own loop
        tasks = [
            asyncio.create_task(self._poll_loop(provider))
            for provider in self.providers
        ]

        # Run all provider loops concurrently, forever
        await asyncio.gather(*tasks)

    async def _poll_loop(self, provider: ProviderConfig):
        """
        Infinite polling loop for a single provider.
        Waits for the configured interval between each poll.
        """
        print(f"[Scheduler] Starting poll loop for '{provider.name}' every {provider.poll_interval_seconds}s")

        while True:
            await self._poll_once(provider)
            await asyncio.sleep(provider.poll_interval_seconds)

    async def _poll_once(self, provider: ProviderConfig):
        """
        Single poll cycle for one provider:
        fetch → detect → notify → save state
        """

        try:
            # Step 1 — Fetch fresh incidents from the feed
            adapter = self._get_adapter(provider)
            incidents = await adapter.fetch_incidents()

            if not incidents:
                print(f"[Scheduler] No incidents found for '{provider.name}'")
                return

            # Step 2 — Detect what changed
            events = await self.detector.detect(incidents)

            # Step 3 — Notify for each change
            for event in events:
                for notifier in self.notifiers:
                    try:
                        await notifier.notify(event)
                    except Exception as e:
                        print(f"[Scheduler] Notifier failed for '{provider.name}': {e}")

            # Step 4 — Persist updated state to disk
            await self.state_manager.save()

        except Exception as e:
            print(f"[Scheduler] Error polling '{provider.name}': {e}")

    def _get_adapter(self, provider: ProviderConfig):
        """
        Returns the appropriate adapter based on feed_type.
        Add new adapters here as you support more feed types.
        """
        if provider.feed_type in ("atom", "rss"):
            return AtomAdapter(
                provider_name=provider.name,
                feed_url=provider.feed_url
            )
        else:
            raise ValueError(f"Unsupported feed type: {provider.feed_type}")
