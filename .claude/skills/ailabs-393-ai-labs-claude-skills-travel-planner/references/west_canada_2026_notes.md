# Western Canada — Operational Notes

Regional reference for an Alberta + BC road trip. Independent of the
current plan in `trip.md` — used as background when the plan changes.

> **Prefer live data:** for distances, drive times, lodging, and campsite
> availability, call the Mapbox / Airbnb / Campertunity MCPs (see SKILL.md).
> The numbers below are rough fallbacks only.

## Live-data tool routing

| Question                                    | Tool                                          |
| ------------------------------------------- | --------------------------------------------- |
| Drive time / distance between two places   | `mapbox_directions_tool`                      |
| Compare drive times to several candidates  | `mapbox_matrix_tool`                          |
| Find a place by name / category            | `mapbox_search_and_geocode_tool`, `mapbox_category_search_tool` |
| Reorder a multi-stop day                   | `mapbox_optimization_tool`                    |
| What's reachable in N hours                | `mapbox_isochrone_tool`                       |
| Map snapshot for `trip.md`                 | `mapbox_static_map_image_tool`                |
| Hotel / Airbnb for a non-camping night     | `airbnb_search`, `airbnb_listing`             |
| Campsite for a non-Parks-Canada night      | `campertunity_listing-search`, `*-availability`, `*-details` |

## Driving distances (rough fallbacks — verify with Mapbox)

- Calgary (YYC) → Banff: ~130 km / ~1h30
- Banff → Lake Louise: ~60 km / ~45 min
- Lake Louise → Jasper (Icefields Parkway): ~230 km / ~3h30 driving (allow 5–7h with stops)
- Jasper → Hinton: ~80 km / ~1h
- Hinton → Rocky Pass / South Boundary trailhead: ~1h on forestry roads (recheck conditions)
- Hinton → Valemount: ~200 km / ~2h30
- Valemount → Wells Gray (Clearwater): ~130 km / ~1h30
- Clearwater → Squamish: ~670 km / ~8h (split this drive)
- Squamish → Vancouver (downtown): ~70 km / ~1h
- Vancouver → Richmond / YVR: ~25 km / ~30 min

## Reservations to consider (whenever they appear in the plan)

- **Campsites:** check Campertunity first via `campertunity_listing-search` + `*-availability`. For Parks Canada / BC Parks frontcountry (Tunnel Mountain, Lake Louise, Whistlers, Wapiti, Porteau Cove, etc.), Campertunity often won't have inventory — fall back to the official reservation systems.
- **Backcountry permits** (South Boundary, Skoki, Berg Lake, etc.): separate Parks Canada window, often opens January — official site only.
- **Moraine Lake shuttle:** only legal way in for sunrise; sells out months ahead — official Parks Canada / Roam Transit channels only.
- **Recovery / city nights** (mid-trip washer-dryer, final night near YVR): use `airbnb_search` for the current dates and group size in `trip.md`.

## Backcountry — bear country

- Bear spray cannot be flown. Buy on arrival in Calgary (Canadian Tire, MEC, Atmosphere, used via Bow Valley Facebook groups, HI Calgary donation bin).
- Stove fuel canisters: same rule, buy on arrival.
- Use Parks Canada-approved bear hang or bear canister where required.
- Cook 100m+ downwind from sleeping area; food + toiletries hung or canistered.
- Make noise on trail; groups do this naturally.
- Carry spray accessible at hip/chest, not buried in the pack.

## Money

- Domestic Canada — CAD only, no exchange.
- Tap accepted almost everywhere; carry $50-100 cash for forestry roads, small-town gas pumps, tip jars.

## Safety

- Vancouver: vehicle break-ins are very common. If gear is staying in a vehicle in the city, conceal everything (tarp / cargo cover) and prefer a paid garage to street parking.
- Wildfire smoke: check BC Wildfire and Alberta Wildfire dashboards 7 days ahead. Have a backup plan (e.g. shift south to the Kootenays) if the planned region is impacted.
- Cell coverage drops out across long sections of the Icefields Parkway and most backcountry. A satellite communicator (InReach or equivalent) is mandatory for any backcountry leg.

## Useful links

- Parks Canada (Banff, Jasper, Yoho, Kootenay): parks.canada.ca
- BC Parks reservations: bcparks.ca/reservations
- DriveBC (road closures): drivebc.ca
- Alberta 511 (road conditions): 511.alberta.ca
- BC Wildfire dashboard: wildfiresituation.nrs.gov.bc.ca
- AB Wildfire status: wildfire.alberta.ca
- AdventureSmart trip planning: adventuresmart.ca
