#!/usr/bin/env python3
"""
West Canada 2026 Trip DB

Storage for the locked-in trip's preferences, expense tracking, and
itinerary tweaks. Scoped to the single Alberta -> BC trip in trip.md.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

DB_DIR = Path.home() / ".claude" / "travel_planner"
PREFERENCES_FILE = DB_DIR / "preferences.json"
TRIPS_FILE = DB_DIR / "trips.json"


def ensure_db_files() -> None:
    """Ensure all database files exist."""
    DB_DIR.mkdir(parents=True, exist_ok=True)

    if not PREFERENCES_FILE.exists():
        default_prefs = {
            "initialized": False,
            "created_at": datetime.now().isoformat(),
            "trip_name": "",
            "travel_style": "",
            "budget_level": "",
            "pace_preference": "",
            "group_size": 0,
            "vehicles": [],
            "accommodation_pattern": "",
            "passes": [],
            "languages": []
        }
        PREFERENCES_FILE.write_text(json.dumps(default_prefs, indent=2))

    if not TRIPS_FILE.exists():
        default_trips = {
            "current_trips": [],
            "past_trips": [],
            "trip_ideas": []
        }
        TRIPS_FILE.write_text(json.dumps(default_trips, indent=2))


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON from file."""
    ensure_db_files()
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_json(file_path: Path, data: Dict[str, Any]) -> None:
    """Save JSON to file."""
    ensure_db_files()
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


# ============================================================================
# PREFERENCES MANAGEMENT
# ============================================================================

def is_initialized() -> bool:
    """Check if travel preferences are initialized."""
    prefs = load_json(PREFERENCES_FILE)
    return prefs.get("initialized", False)


def get_preferences() -> Dict[str, Any]:
    """Get user travel preferences."""
    return load_json(PREFERENCES_FILE)


def save_preferences(preferences: Dict[str, Any]) -> None:
    """Save user travel preferences."""
    prefs = load_json(PREFERENCES_FILE)
    prefs.update(preferences)
    prefs["initialized"] = True
    prefs["last_updated"] = datetime.now().isoformat()
    save_json(PREFERENCES_FILE, prefs)


def update_preference(key: str, value: Any) -> None:
    """Update a specific preference."""
    prefs = load_json(PREFERENCES_FILE)
    prefs[key] = value
    prefs["last_updated"] = datetime.now().isoformat()
    save_json(PREFERENCES_FILE, prefs)


# ============================================================================
# TRIP MANAGEMENT
# ============================================================================

def get_trips(status: str = "all") -> Dict[str, List[Dict]]:
    """
    Get trips by status.

    Args:
        status: "current", "past", "ideas", or "all"
    """
    trips = load_json(TRIPS_FILE)

    if status == "all":
        return trips
    elif status in ["current", "past", "ideas"]:
        key = f"{status}_trips" if status != "ideas" else "trip_ideas"
        return {key: trips.get(key, [])}
    return {}


def add_trip(trip: Dict[str, Any], status: str = "current") -> str:
    """
    Add a new trip.

    Args:
        trip: Trip data
        status: "current", "past", or "idea"

    Returns:
        Trip ID
    """
    trips = load_json(TRIPS_FILE)

    trip_id = str(datetime.now().timestamp())
    trip["id"] = trip_id
    trip["created_at"] = datetime.now().isoformat()

    if status == "current":
        trips["current_trips"].append(trip)
    elif status == "past":
        trips["past_trips"].append(trip)
    elif status == "idea":
        trips["trip_ideas"].append(trip)

    save_json(TRIPS_FILE, trips)
    return trip_id


def update_trip(trip_id: str, updates: Dict[str, Any]) -> bool:
    """Update a trip."""
    trips = load_json(TRIPS_FILE)

    for trip_list in [trips["current_trips"], trips["past_trips"], trips["trip_ideas"]]:
        for trip in trip_list:
            if trip.get("id") == trip_id:
                trip.update(updates)
                trip["updated_at"] = datetime.now().isoformat()
                save_json(TRIPS_FILE, trips)
                return True
    return False


def get_trip_by_id(trip_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific trip by ID."""
    trips = load_json(TRIPS_FILE)

    for trip_list in [trips["current_trips"], trips["past_trips"], trips["trip_ideas"]]:
        for trip in trip_list:
            if trip.get("id") == trip_id:
                return trip
    return None


def move_trip_to_past(trip_id: str) -> bool:
    """Move a current trip to past trips."""
    trips = load_json(TRIPS_FILE)

    for i, trip in enumerate(trips["current_trips"]):
        if trip.get("id") == trip_id:
            trip["completed_at"] = datetime.now().isoformat()
            trips["current_trips"].pop(i)
            trips["past_trips"].append(trip)
            save_json(TRIPS_FILE, trips)
            return True
    return False


def delete_trip(trip_id: str) -> bool:
    """Delete a trip."""
    trips = load_json(TRIPS_FILE)

    for trip_list in [trips["current_trips"], trips["past_trips"], trips["trip_ideas"]]:
        for i, trip in enumerate(trip_list):
            if trip.get("id") == trip_id:
                trip_list.pop(i)
                save_json(TRIPS_FILE, trips)
                return True
    return False


# ============================================================================
# BUDGET TRACKING
# ============================================================================

def add_expense(trip_id: str, expense: Dict[str, Any]) -> bool:
    """Add an expense to a trip."""
    trips = load_json(TRIPS_FILE)

    for trip_list in [trips["current_trips"], trips["past_trips"]]:
        for trip in trip_list:
            if trip.get("id") == trip_id:
                if "expenses" not in trip:
                    trip["expenses"] = []

                expense["id"] = datetime.now().timestamp()
                expense["date"] = expense.get("date", datetime.now().isoformat())
                trip["expenses"].append(expense)

                # Update total spent
                if "budget" not in trip:
                    trip["budget"] = {}

                total = sum(e.get("amount", 0) for e in trip["expenses"])
                trip["budget"]["spent"] = total

                save_json(TRIPS_FILE, trips)
                return True
    return False


def get_trip_expenses(trip_id: str) -> List[Dict[str, Any]]:
    """Get all expenses for a trip."""
    trip = get_trip_by_id(trip_id)
    if trip:
        return trip.get("expenses", [])
    return []


def get_budget_summary(trip_id: str) -> Dict[str, Any]:
    """Get budget summary for a trip."""
    trip = get_trip_by_id(trip_id)
    if not trip:
        return {}

    budget = trip.get("budget", {})
    expenses = trip.get("expenses", [])

    total_budget = budget.get("total", 0)
    spent = sum(e.get("amount", 0) for e in expenses)
    remaining = total_budget - spent

    # Category breakdown
    categories = {}
    for expense in expenses:
        category = expense.get("category", "Other")
        categories[category] = categories.get(category, 0) + expense.get("amount", 0)

    return {
        "total_budget": total_budget,
        "spent": spent,
        "remaining": remaining,
        "percentage_used": (spent / total_budget * 100) if total_budget > 0 else 0,
        "by_category": categories
    }


# ============================================================================
# ITINERARY MANAGEMENT
# ============================================================================

def add_itinerary_item(trip_id: str, item: Dict[str, Any]) -> bool:
    """Add an item to trip itinerary."""
    trips = load_json(TRIPS_FILE)

    for trip in trips["current_trips"]:
        if trip.get("id") == trip_id:
            if "itinerary" not in trip:
                trip["itinerary"] = []

            item["id"] = datetime.now().timestamp()
            trip["itinerary"].append(item)

            # Sort by date
            trip["itinerary"].sort(key=lambda x: x.get("date", ""))

            save_json(TRIPS_FILE, trips)
            return True
    return False


def get_itinerary(trip_id: str) -> List[Dict[str, Any]]:
    """Get trip itinerary."""
    trip = get_trip_by_id(trip_id)
    if trip:
        return trip.get("itinerary", [])
    return []


# ============================================================================
# STATISTICS & INSIGHTS
# ============================================================================

def get_trip_stats() -> Dict[str, Any]:
    """Stats for the West Canada 2026 trip (current or past)."""
    trips = load_json(TRIPS_FILE)
    all_trips = trips.get("current_trips", []) + trips.get("past_trips", [])

    if not all_trips:
        return {"trips": 0}

    trip = all_trips[0]
    expenses = trip.get("expenses", [])
    spent = sum(e.get("amount", 0) for e in expenses)
    budget_total = trip.get("budget", {}).get("total", 0)

    by_category = {}
    by_phase = {}
    for e in expenses:
        cat = e.get("category", "other")
        phase = e.get("phase", "unspecified")
        by_category[cat] = by_category.get(cat, 0) + e.get("amount", 0)
        by_phase[phase] = by_phase.get(phase, 0) + e.get("amount", 0)

    return {
        "trip_name": trip.get("name", "West Canada 2026"),
        "status": "current" if trip in trips.get("current_trips", []) else "past",
        "duration_days": trip.get("duration_days", 13),
        "group_size": trip.get("travelers", 7),
        "budget_total_cad": budget_total,
        "spent_cad": spent,
        "remaining_cad": budget_total - spent,
        "percentage_used": round((spent / budget_total * 100), 2) if budget_total else 0,
        "by_category": by_category,
        "by_phase": by_phase,
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def export_all() -> Dict[str, Any]:
    """Export all travel data."""
    return {
        "preferences": get_preferences(),
        "trips": get_trips("all"),
        "stats": get_trip_stats(),
        "exported_at": datetime.now().isoformat()
    }


def reset_all() -> None:
    """Reset all data (use with caution)."""
    for file_path in [PREFERENCES_FILE, TRIPS_FILE]:
        if file_path.exists():
            file_path.unlink()
    ensure_db_files()


# ============================================================================
# CLI INTERFACE
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Travel Planner Database Manager")
        print("\nUsage:")
        print("  python3 travel_db.py is_initialized")
        print("  python3 travel_db.py get_preferences")
        print("  python3 travel_db.py get_trips [current|past|ideas|all]")
        print("  python3 travel_db.py stats")
        print("  python3 travel_db.py export")
        print("  python3 travel_db.py reset")
        sys.exit(1)

    command = sys.argv[1]

    if command == "is_initialized":
        print("true" if is_initialized() else "false")
    elif command == "get_preferences":
        print(json.dumps(get_preferences(), indent=2))
    elif command == "get_trips":
        status = sys.argv[2] if len(sys.argv) > 2 else "all"
        print(json.dumps(get_trips(status), indent=2))
    elif command == "stats":
        print(json.dumps(get_trip_stats(), indent=2))
    elif command == "export":
        print(json.dumps(export_all(), indent=2))
    elif command == "reset":
        confirm = input("Are you sure you want to reset all travel data? (yes/no): ")
        if confirm.lower() == "yes":
            reset_all()
            print("All travel data has been reset.")
        else:
            print("Reset cancelled.")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
