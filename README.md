# 📡 Status Tracker

A lightweight, event-driven Python system that monitors status pages from any provider and instantly notifies you when a new incident or outage is detected — without inefficient polling.

---

## ✨ Features

- **Provider agnostic** — track any Atom/RSS based status page (OpenAI, GitHub, Cloudflare, Stripe, and more)
- **Event driven change detection** — only triggers when something actually changes, no noise
- **Async concurrent polling** — all providers are monitored simultaneously via `asyncio`, a slow feed never blocks others
- **Persistent state** — remembers seen incidents across restarts, no duplicate alerts
- **Pluggable notifiers** — ships with Console output, easily extend to Slack, webhooks, email
- **Config driven** — add a new provider by editing one YAML file, zero code changes needed

---

## 🗂 Project Structure

```
status-tracker/
│
├── config/
│   ├── providers.yaml          # All provider definitions live here
│   └── config_loader.py        # Reads and validates the YAML config
│
├── adapters/
│   └── atom_adapter.py         # Fetches and parses Atom/RSS feeds
│
├── core/
│   ├── change_detector.py      # Diffs incoming incidents against stored state
│   ├── scheduler.py            # Async polling engine, wires all components
│   └── state_manager.py        # Loads and saves state.json
│
├── notifiers/
│   ├── base.py                 # Abstract base class all notifiers must implement
│   └── console_notifier.py     # Prints formatted alerts to stdout
│
├── models/
│   └── incident.py             # Normalized incident data model
│
├── main.py                     # Entry point
├── requirements.txt
└── state.json                  # Auto-generated, do not edit manually
```

---

## ⚙️ How It Works

### Startup Sequence (runs once)

```
python main.py
      │
      ├── 1. Load providers.yaml       → parse all provider configs
      ├── 2. Load state.json           → restore memory of seen incidents
      ├── 3. Initialize notifiers      → ConsoleNotifier (+ any others)
      ├── 4. Initialize Scheduler      → wire adapter + detector + notifier
      └── 5. scheduler.run()           → launch one async loop per provider
```

### Poll Cycle (repeats every N seconds per provider)

```
Scheduler._poll_once("OpenAI")
      │
      ├── 1. AtomAdapter.fetch_incidents()
      │        └── async HTTP GET → parse XML → return List[Incident]
      │
      ├── 2. _parse_entry() for each <entry>
      │        ├── extract status      from <b>Status: ...</b>
      │        ├── extract services    from <li> tags
      │        └── extract message     from remaining plain text
      │
      ├── 3. ChangeDetector.detect(incidents)
      │        └── for each Incident → is_new()? is_updated()? → build IncidentEvent
      │
      ├── 4. ConsoleNotifier.notify(event)
      │        └── only fires if events list is non-empty
      │
      └── 5. StateManager.save()
               └── persist updated state to state.json
```

### Change Detection Logic

| Condition | Action |
|---|---|
| `incident_id` not found in state |  **NEW** — create event, notify, upsert to state |
| `incident_id` exists but `updated_at` changed | **UPDATE** — create event with old + new, notify, upsert |
| `incident_id` exists and `updated_at` identical | **SKIP** — no event, silent poll |

### Async Concurrency

All providers run on independent `asyncio` tasks launched by `asyncio.gather()`. Each task has its own polling interval defined in `providers.yaml`. A slow or unreachable feed from one provider never delays the others.

```
asyncio.gather(
    _poll_loop("OpenAI"),      # every 60s
    _poll_loop("GitHub"),      # every 60s
    _poll_loop("Cloudflare"),  # every 60s
    _poll_loop("Stripe"),      # every 60s
)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- `pip`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/status-tracker.git
cd status-tracker

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

---

## 📦 Dependencies

```
feedparser        # Parses Atom/RSS XML feeds
aiohttp           # Async HTTP client for concurrent feed fetching
aiofiles          # Async file I/O for non-blocking state persistence
pyyaml            # Reads providers.yaml config file
beautifulsoup4    # Parses HTML embedded inside Atom feed content
```
