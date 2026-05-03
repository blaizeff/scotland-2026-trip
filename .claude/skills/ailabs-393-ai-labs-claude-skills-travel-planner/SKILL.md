---
name: travel-planner
description: Trip planning assistant for the West Canada road trip project. Helps with itinerary, camping/backcountry logistics, budget tracking, and packing checklists. The live plan lives in trip.md at the project root — read it every time, since everything except the locked backcountry trek nights is open to change. Uses the Mapbox, Airbnb, and Campertunity MCPs for live routing, lodging, and campsite data.
---

# Travel Planner — West Canada Trip

## Source of Truth

The live trip plan is in `trip.md` at the project root. **Read it every time before responding.** Treat its contents as the current state of the plan; this skill only adds tooling and reference material around it.

## Locked Items

The only things that are firm:

- **Backcountry trek campsites** — Medicine Tent and La Grace nights along the South Boundary Trail (Rocky Pass access), reserved with Parks Canada and not movable.

Everything else — dates, flights, group size, vehicles, route, budget, accommodation choices, activities — is editable.

## Use Live MCP Data, Not Static Estimates

This project has three MCPs installed. **Prefer them over hardcoded numbers** any time the user is making a real decision (booking, comparing options, validating a plan). The static notes in `references/` are only fallbacks.

### Mapbox MCP — routing, distances, places

Use for any real-world geography question.

- `mapbox_directions_tool` — drive time and route between two specific places (e.g. Banff campground → Jasper townsite). Always pass current waypoints from `trip.md`, never assume.
- `mapbox_matrix_tool` — drive-time matrix when comparing several candidate stops at once.
- `mapbox_distance_tool` / `mapbox_length_tool` — straight-line or path distances.
- `mapbox_search_and_geocode_tool` — turn a place name (e.g. "Wells Gray Helmcken Falls", "Stawamus Chief trailhead") into coordinates.
- `mapbox_category_search_tool` + `mapbox_category_list_tool` — find gas stations, grocery stores, outdoor stores along the route (e.g. MEC Calgary on arrival).
- `mapbox_isochrone_tool` — "what's reachable within 2h of Squamish" type questions when proposing alternatives.
- `mapbox_optimization_tool` — when the user wants to reorder a multi-stop day.
- `mapbox_static_map_image_tool` — generate a route map to embed in `trip.md`.
- `mapbox_reverse_geocode_tool` — name a coordinate (e.g. for a trailhead pin).

When asked "how long does X → Y take" or "what's near Z", call Mapbox. Do not pull from the static distance table in `references/`.

### Airbnb MCP — recovery / city accommodations

Use for any night that is not camping.

- `airbnb_search` — find listings near a location for given dates and group size. Always pass the current group size from `trip.md` (do not assume 7).
- `airbnb_listing` — full details on a candidate listing (amenities, washer/dryer for recovery nights, cancellation policy, total price).
- `airbnb_maps_*` — Airbnb's bundled mapping helpers if Mapbox isn't already in scope for the question.

Typical use: search for the recovery night between phases (washer/dryer is usually a hard requirement after the trek), and the final night near YVR.

### Campertunity MCP — campsites & availability

Use for camping nights that are not already Parks Canada backcountry permits.

- `campertunity_listing-search` — find campsites in a region for the date range and group size.
- `campertunity_listing-details` — site amenities, vehicle access, fire pit, pet rules, etc.
- `campertunity_listing-availability` — check live availability for the dates currently in `trip.md`.
- `campertunity_listing-book` — only book when the user explicitly asks. **Bookings are paid actions; always confirm price, dates, group size, and cancellation policy in writing first.**

For Parks Canada / BC Parks campgrounds (Tunnel Mountain, Whistlers, Wapiti, Porteau Cove, etc.), Campertunity may not have inventory — fall back to the official reservation systems and just note it for the user.

### Decision rules

- **Distance / drive time?** Mapbox.
- **Hotel-style or short-term rental night?** Airbnb.
- **Campsite night (not already a locked Parks Canada permit)?** Campertunity first; Parks Canada / BC Parks reservation systems if Campertunity comes up empty.
- **Anything else** (visas, currency, weather, fire bans, wildfire smoke): web search.

Always pass current values from `trip.md` (group size, dates, vehicles) into MCP calls. Do not let the previously-encoded "7 adults / Jul 26 – Aug 7" leak into queries — read the file fresh.

## When to Use This Skill

- Refining or rewriting the itinerary in `trip.md`
- Camping and backcountry logistics
- Group budget shaping and expense tracking
- Packing checklists
- Driving and routing across Alberta and BC (always via Mapbox)
- Comparing accommodation or campsite options for any night

## Workflow

### 1. Read `trip.md`

It is the source of truth for the current state. Pull group size, dates, route, vehicles, and budget from it before any MCP call.

### 2. Live data first, scripts second

For real-world facts (drive times, lodging prices, campsite availability), call the MCPs. The bundled Python scripts handle pure logic (budget percentages, packing structure, timeline math) — they do not know anything about the world.

### 3. Suggest, don't lock

Treat the existing plan as one option. If the user wants to swap a phase, change the route, resize the group, or trade camping for hotels, accommodate it. The trek nights are the only thing that should anchor a discussion.

### 4. Use the helper scripts for arithmetic

```bash
python3 scripts/plan_generator.py budget --per-person 2000 --group-size 7 --duration-days 13
python3 scripts/plan_generator.py packing --climate mountain_summer \
    --activities hiking camping paddleboard hot_springs --backcountry
python3 scripts/plan_generator.py pretrip --departure 2026-07-26
```

### 5. Track expenses (optional)

The `travel_db.py` storage layer can hold preferences, the active trip, and per-trip expenses if useful.

## Constraints to Respect

1. **Do not move the backcountry trek nights** (Medicine Tent + La Grace).
2. **Match `trip.md`** for everything else; do not hardcode dates, group size, vehicles, or route into responses.
3. **Be ready for changes.** The plan is a draft.
4. **Air-travel rules**: bear spray and stove fuel cannot be flown — sourced on arrival. Mention this whenever the plan calls for backcountry gear.
5. **Booking is a paid action.** Never invoke `campertunity_listing-book` (or any future booking tool) without explicit user confirmation including price, dates, and cancellation terms.
6. **Language**: `trip.md` is in French; match the user's language in the current message.

## Resources (bundled with the skill)

- `scripts/travel_db.py` — preferences, trip, expense tracking
- `scripts/plan_generator.py` — budget / packing / pre-trip helpers (all parameterized)
- `references/west_canada_2026_notes.md` — fallback regional reference: gear sourcing, bear safety, wildfire/road dashboards, Vancouver vehicle-security note. Distance table is a rough fallback only — prefer Mapbox.

## CLI cheatsheet

```bash
python3 scripts/travel_db.py is_initialized
python3 scripts/travel_db.py get_preferences
python3 scripts/travel_db.py get_trips current
python3 scripts/travel_db.py stats

python3 scripts/plan_generator.py budget --help
python3 scripts/plan_generator.py packing --help
python3 scripts/plan_generator.py pretrip --help
```

Data is stored at `~/.claude/travel_planner/`.
