#!/usr/bin/env python3
"""
Trip plan helpers.

Functions take parameters; nothing about the current trip is hardcoded.
The only externally-locked anchor for this project is the backcountry trek
(see trip.md). Everything else — dates, group size, budget, vehicles,
itinerary — is editable.
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


# ============================================================================
# BUDGET
# ============================================================================

# Default allocation tuned for a road-trip / fly-and-camp style trip.
# Override by passing your own dict to calculate_budget_breakdown().
DEFAULT_ALLOCATION = {
    "flights":                       0.30,
    "vehicles_fuel_drop_fees":       0.25,
    "camping_fees":                  0.05,
    "recovery_accommodation":        0.10,
    "food_groceries_restaurants":    0.18,
    "activities_extras":             0.05,
    "gear_bought_on_arrival":        0.03,
    "buffer_misc":                   0.04,
}


def calculate_budget_breakdown(per_person: float,
                               group_size: int,
                               duration_days: int,
                               allocation: Optional[Dict[str, float]] = None,
                               currency: str = "CAD") -> Dict[str, Any]:
    """
    Generic group-budget breakdown.

    Args:
        per_person: Budget cap per person.
        group_size: Number of travelers.
        duration_days: Trip length in days.
        allocation: Optional dict of category -> percentage (0-1). Sum should be ~1.0.
                    Defaults to DEFAULT_ALLOCATION.
        currency: Currency code, used only as a label.
    """
    allocation = allocation or DEFAULT_ALLOCATION
    total = per_person * group_size

    breakdown = {}
    for category, pct in allocation.items():
        amount = total * pct
        breakdown[category] = {
            f"total_group_{currency.lower()}": round(amount, 2),
            f"per_person_{currency.lower()}": round(amount / group_size, 2) if group_size else 0,
            "percentage": round(pct * 100, 1),
        }

    return {
        f"total_group_budget_{currency.lower()}": total,
        f"per_person_budget_{currency.lower()}": per_person,
        "group_size": group_size,
        "duration_days": duration_days,
        f"daily_average_per_person_{currency.lower()}": (
            round(per_person / duration_days, 2) if duration_days else 0
        ),
        "breakdown": breakdown,
    }


# ============================================================================
# PACKING
# ============================================================================

def generate_packing_checklist(climate: str = "moderate",
                               activities: Optional[List[str]] = None,
                               include_backcountry: bool = False) -> Dict[str, List[str]]:
    """
    Build a packing checklist by climate + activities.

    Args:
        climate: "warm", "cold", "moderate", "mountain_summer", "tropical", etc.
        activities: list like ["hiking", "camping", "beach", "city", "paddleboard"].
        include_backcountry: add a dedicated backcountry trek section.
    """
    activities = activities or []
    climate_l = climate.lower()
    activities_l = [a.lower() for a in activities]

    checklist: Dict[str, List[str]] = {
        "documents_personal": [
            "ID / driver's license (carry where required for car rentals)",
            "Health card / insurance card",
            "Travel insurance documents",
            "Reservation confirmations",
            "Emergency contact list",
        ],
        "clothing": [],
        "toiletries": [
            "Toothbrush + paste",
            "Soap / shampoo",
            "Deodorant",
            "Sunscreen",
            "Personal care items",
            "Medications",
        ],
        "technology": [
            "Phone + charger",
            "Power bank",
            "Headlamp + spare batteries",
            "Camera (optional)",
            "Offline maps downloaded",
        ],
        "activities": [],
    }

    # Climate-driven clothing
    if "tropical" in climate_l or "warm" in climate_l:
        checklist["clothing"] = [
            "Light breathable tops",
            "Shorts",
            "Swimsuit",
            "Sun hat", "Sunglasses",
            "Sandals",
        ]
    elif "cold" in climate_l or "winter" in climate_l:
        checklist["clothing"] = [
            "Insulated jacket",
            "Mid-layer / fleece",
            "Thermal base layers",
            "Warm socks",
            "Gloves + tuque",
            "Winter boots",
        ]
    elif "mountain" in climate_l:
        checklist["clothing"] = [
            "Merino / synthetic t-shirts",
            "Hiking pants (1-2)",
            "Shorts",
            "Fleece / mid-layer",
            "Rain shell (Gore-Tex)",
            "Light tuque + gloves (cold mountain nights)",
            "Wool socks (3-4 pairs)",
            "Quick-dry underwear",
            "Broken-in hiking boots",
            "Camp sandals",
        ]
    else:  # moderate
        checklist["clothing"] = [
            "Mix of layers",
            "T-shirts + long-sleeve",
            "Pants + shorts",
            "Light jacket",
            "Comfortable walking shoes",
        ]

    # Activity add-ons
    activity_items = {
        "hiking": ["Day pack", "Trekking poles", "Reusable water bottle", "Trail snacks"],
        "camping": [
            "Tent",
            "Sleeping bag (3-season)",
            "Sleeping pad",
            "Stove + fuel (buy fuel locally if flying)",
            "Cookset + utensils",
            "Cooler",
            "Camp chair",
            "Tarp",
        ],
        "beach": ["Swimsuit", "Beach towel", "Dry bag"],
        "paddleboard": ["Swimsuit", "Quick-dry layer", "Water shoes", "Dry bag"],
        "biking": ["Helmet", "Cycling layer", "Padded shorts (optional)"],
        "city": ["One smart-casual outfit", "Comfortable city shoes"],
        "hot_springs": ["Swimsuit", "Quick-dry towel"],
    }
    for a in activities_l:
        for key, items in activity_items.items():
            if key in a:
                checklist["activities"].extend(items)

    # Backcountry block (separate so it does not pollute frontcountry list)
    if include_backcountry:
        checklist["backcountry_trek"] = [
            "Backpacking pack (50-65L)",
            "Bear spray (buy locally — cannot fly with it)",
            "Stove fuel canisters (buy locally)",
            "Lightweight stove + pot",
            "Water filter or treatment tablets",
            "Dehydrated meals",
            "Bear-hang rope or approved bear canister",
            "First aid kit",
            "Satellite communicator (e.g. InReach)",
            "Topo maps + offline GPS",
            "Trekking poles",
        ]

    # Dedupe each list
    for k, v in checklist.items():
        seen = set()
        deduped = []
        for item in v:
            if item not in seen:
                deduped.append(item)
                seen.add(item)
        checklist[k] = deduped

    return checklist


# ============================================================================
# PRE-TRIP TIMELINE
# ============================================================================

DEFAULT_TIMELINE = [
    (60, [
        "Confirm flights, vehicle rentals, drop-off locations and fees",
        "Reserve frontcountry campsites (Parks Canada / BC Parks open windows fast)",
        "Reserve recovery accommodations (mid-trip + final night near airport)",
        "Reserve any required shuttles (e.g. Moraine Lake)",
    ]),
    (30, [
        "Book backcountry permits if not already locked",
        "Inventory group gear; identify gaps",
        "Check fire bans / backcountry conditions",
        "Travel insurance with backcountry coverage if applicable",
        "Start prepping any home-prepared trail food",
    ]),
    (14, [
        "Final grocery + meal prep",
        "Print backcountry permit + share emergency plan with the group",
        "Identify on-arrival sources for bear spray, fuel, coolers",
        "Confirm satellite comms plan (InReach, etc.)",
    ]),
    (7, [
        "Online check-in 24h before flight",
        "Pack — distribute heavy gear by vehicle",
        "Charge satcom, headlamps, power banks",
        "Download offline maps for the route",
    ]),
    (1, [
        "Re-check departure time",
        "Prep carry-ons (NO bear spray, NO fuel canisters in air travel)",
        "Set multiple alarms",
    ]),
]


def generate_pre_trip_checklist(departure_date: str,
                                today: Optional[datetime] = None,
                                custom_timeline: Optional[List[tuple]] = None
                                ) -> Dict[str, Any]:
    """
    Generic pre-trip timeline anchored to a departure date.

    Args:
        departure_date: ISO date string (YYYY-MM-DD).
        today: Override "now" for testing.
        custom_timeline: Override the default list of (days_before, [tasks...]) tuples.
    """
    today = today or datetime.now()
    try:
        departure = datetime.fromisoformat(departure_date)
    except ValueError:
        raise ValueError(f"departure_date must be ISO format (YYYY-MM-DD), got {departure_date!r}")

    timeline_def = custom_timeline or DEFAULT_TIMELINE
    days_until = (departure - today).days

    timeline = []
    for days_before, tasks in timeline_def:
        anchor = departure - timedelta(days=days_before)
        due_in = (anchor - today).days
        timeline.append({
            "milestone": f"{days_before} days before",
            "anchor_date": anchor.date().isoformat(),
            "due_in_days": due_in,
            "status": "upcoming" if due_in >= 0 else "past_due",
            "tasks": tasks,
        })

    return {
        "departure": departure.date().isoformat(),
        "days_until_departure": days_until,
        "timeline": timeline,
    }


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generic trip plan helpers')
    sub = parser.add_subparsers(dest='cmd')

    b = sub.add_parser('budget', help='Print budget breakdown')
    b.add_argument('--per-person', type=float, required=True)
    b.add_argument('--group-size', type=int, required=True)
    b.add_argument('--duration-days', type=int, required=True)
    b.add_argument('--currency', default='CAD')

    p = sub.add_parser('packing', help='Print packing checklist')
    p.add_argument('--climate', default='moderate')
    p.add_argument('--activities', nargs='*', default=[])
    p.add_argument('--backcountry', action='store_true')

    pre = sub.add_parser('pretrip', help='Print pre-trip timeline')
    pre.add_argument('--departure', required=True, help='ISO date YYYY-MM-DD')

    args = parser.parse_args()

    if args.cmd == 'budget':
        print(json.dumps(
            calculate_budget_breakdown(args.per_person, args.group_size,
                                       args.duration_days, currency=args.currency),
            indent=2, ensure_ascii=False))
    elif args.cmd == 'packing':
        print(json.dumps(
            generate_packing_checklist(args.climate, args.activities, args.backcountry),
            indent=2, ensure_ascii=False))
    elif args.cmd == 'pretrip':
        print(json.dumps(
            generate_pre_trip_checklist(args.departure),
            indent=2, ensure_ascii=False, default=str))
    else:
        parser.print_help()
