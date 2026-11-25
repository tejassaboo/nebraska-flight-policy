# University of Nebraska Travel Policy Flight Booking

**No affiliation with the University of Nebraska.** The handbook is the University of Nebraska system's public
*Travel Policy* (effective 2018 by campus, last revised March 7, 2019), bundled verbatim for research. Its source URL
was not recorded when the PDF was downloaded (`pilot_work/originals/MANIFEST.md`: UNVERIFIED); confirm the public URL
before publishing this plugin.

A `nanoagent.plugin/v0001` plugin. An agent handles one traveller's flight request under the university's real travel
policy: it reads the trip record, searches a simulated flight world and submits **BOOK**, **REFUSE** or
**FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and policy section. A deterministic Python verifier,
with no LLM, rebuilds the offers and the policy's answer itself and checks every field. Built from the
original-handbook template (`handbook_plugins/_template`); `tests/build_scenarios.py` writes the scenario files.

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 6,241 words, 806 lines, sha256 `fe3ec93c...e5431d`, equal to
`pilot_work/originals/nebraska/frozen/SHA256SUMS`) is never paraphrased, and the task text restates no rule. Under
stock NanoAgent the agent does not see it: the plugin then runs as the `off` baseline. The `harness.policy` switch of
the NanoAgent fork (github.com/tejassaboo/nanoagent, branch `policy-switch`) adds it to the system prompt:
`harness.policy: full` adds all of it, and the selection methods add parts of it. These plugins are meant to run with
`query: instructions+input`, so a selector sees the traveller's request.

**Size.** On the paid Thornton/NJC calibration (about 0.2 tokens a character of policy plus 1,800 for the rest of the
first prompt), the first call under `full` is about 10,200 input tokens (42,108 characters of policy), the second
about 11,000 (plus the trip record) and the third 11,500 to 12,500 (plus 2 to 8 offers). A 3-call run (`get_trip`,
`search_flights`, `submit`) is about 33,000 to 34,500 input tokens, near 48,000 with the final message and output:
under the hosted cap of 65,536, with room for one extra tool call.

## Task

- **Input:** `TaskInput`: `scenario` (one of 24 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on the trip's route and date, then `submit` (3 of the 6 hosted steps).
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when refusing),
  `reason_code`, `approver` and `clause`, each from a closed list. The reason list is shared by every handbook plugin
  and holds codes for rules this policy lacks, plus decoy codes from other handbooks' rules.
- **Success:** every field is one the answer key accepts. Score = fields right / 6.

What the policy decides (frozen lines): a Pre-Trip Request approved by the Supervisor Approver and the Financial
Approver before any booking (136-146), a Blanket Travel Authorization only for travel within city limits, a 100-mile
radius or the state (172-181), International Travel (defined at 53-55) with the Vice Chancellor of Business and
Finance's approval (151-153), chartered planes only with that approval (156-158, 316-321), the contracted travel
agency for international flights and a same-day cheaper comparison to buy domestic air outside it (222-235), a ticket
not above the coach or main cabin price with an explanation for any fare that is not the lowest (237-239), the most
economical means that meet the trip's goals (160-162), upgrades at the traveller's own cost (241-247), documented ADA
exemptions (118-123), contracted speakers under the same policy (102-106), and no payment for personal travel or
companions (26-28, 163-170, appendix 762-764).

| Scenario | Category | Expected decision (offer) | Reason | Approver | Clause cited (frozen lines) |
|---|---|---|---|---|---|
| `birch-lantern` | easy | BOOK (delta-economy, ECONOMY) | LOWEST_FARE | SUPERVISOR_APPROVER, FINANCIAL_APPROVER or NONE | AIR_BOOKING etc. (143-145, 237-239) |
| `cobalt-meadow` | easy | BOOK (jetblue-economy, ECONOMY) | UPGRADE_NOT_ELIGIBLE or TRAVELER_PAYS_UPGRADE | same | AIR_BOOKING or UPGRADES (237-239) |
| `dune-sparrow` | easy | BOOK (british-economy, ECONOMY) | LOWEST_FARE | same or VICE_CHANCELLOR_BUSINESS_FINANCE | AIR_BOOKING etc., INTERNATIONAL_TRAVEL (151-153) |
| `ember-thicket` | easy | BOOK (united-economy, ECONOMY) | LOWEST_FARE | request roles or NONE | AIR_BOOKING etc. (237-239) |
| `fern-gable` | easy | BOOK (chicago-economy, ECONOMY) | LOWEST_FARE | request roles or NONE | AIR_BOOKING etc. (160-162, 237-239) |
| `garnet-reed` | boundary_twin | BOOK (morning-premium, PREMIUM_ECONOMY) | PREMIUM_ECONOMY_ALLOWED, LOWEST_FARE or UPGRADE_WITHIN_FARE_MARGIN | request roles or NONE | AIR_BOOKING, UPGRADES or MOST_ECONOMICAL_RATES (237-239) |
| `heron-slate` | boundary_twin | BOOK (morning-economy, ECONOMY) | UPGRADE_NOT_ELIGIBLE or TRAVELER_PAYS_UPGRADE | request roles or NONE | AIR_BOOKING or UPGRADES (237-239) |
| `iris-copper` | boundary_twin | BOOK (minneapolis-economy, ECONOMY) | LOWEST_FARE | request roles or NONE | AIR_BOOKING etc. (160-162) |
| `juniper-wold` | boundary_twin | BOOK (jetblue-economy, ECONOMY) | ARRIVAL_NEEDED_FOR_BUSINESS or LOWEST_FARE | request roles or NONE | MOST_ECONOMICAL_RATES etc. (160-162, 237-239) |
| `kestrel-moor` | boundary_twin | BOOK (dulles-economy, ECONOMY) | LOWEST_FARE | request roles, VC or NONE | AIR_BOOKING etc. (160-162, 151-153) |
| `linden-shoal` | boundary_twin | BOOK (lufthansa-economy, ECONOMY) | ARRIVAL_NEEDED_FOR_BUSINESS or LOWEST_FARE | request roles, VC or NONE | MOST_ECONOMICAL_RATES etc. (160-162) |
| `maple-cinder` | multi_rule | BOOK (airfrance-economy, ECONOMY) | TRAVEL_AGENCY_REQUIRED | request roles, VC or NONE | AIR_BOOKING, APPENDIX_RECEIPTS, INTERNATIONAL_TRAVEL (222-225, 563-567) |
| `nutmeg-ridge` | multi_rule | BOOK (ana-economy, ECONOMY) | TRAVELER_PAYS_UPGRADE or UPGRADE_NOT_ELIGIBLE | request roles, VC or NONE | AIR_BOOKING, UPGRADES, INTERNATIONAL_TRAVEL (237-244) |
| `opal-fjord` | multi_rule | BOOK (united-economy, ECONOMY) | PRIVATE_AIRCRAFT_NOT_APPROVED or LOWEST_FARE | request roles or NONE | PRE_TRIP_APPROVAL, OTHER_FORMS_OF_TRAVEL, COMMERCIAL_AIR or MOST_ECONOMICAL_RATES (156-158, 208-213, 316-321) |
| `pewter-glen` | multi_rule | BOOK (southwest-economy, ECONOMY) | OUTSIDE_FARE_COMPARISON_NOT_MET or TRAVEL_AGENCY_REQUIRED | request roles or NONE | AIR_BOOKING or APPENDIX_RECEIPTS (228-234) |
| `quartz-bramble` | hidden_clause | BOOK (alaska-economy, ECONOMY) | UPGRADE_NOT_ELIGIBLE or TRAVELER_PAYS_UPGRADE | request roles or NONE | NON_UNIVERSITY_PERSONNEL, AIR_BOOKING, UPGRADES (103-106) |
| `russet-dell` | hidden_clause | BOOK (midday-business, BUSINESS) | POLICY_EXEMPTION_DOCUMENTED or MEDICAL_NEED | request roles, ADA_COORDINATOR, UNIVERSITY_TRAVEL_OFFICE or NONE | COMPLIANCE_AND_EXEMPTIONS, MOST_ECONOMICAL_RATES or PRE_TRIP_APPROVAL (118-123, 162) |
| `sorrel-pike` | distractor | BOOK (klm-economy, ECONOMY) | LOWEST_FARE | request roles, VC or NONE | AIR_BOOKING etc., INTERNATIONAL_TRAVEL (151-153; 148-151 is the distractor) |
| `tansy-bluff` | distractor | BOOK (american-economy, ECONOMY) | LOWEST_FARE | request roles, ADA_COORDINATOR or NONE | AIR_BOOKING etc. (237-239; 118-120 is the distractor) |
| `umber-loch` | refusal | REFUSE | COMPANION_NOT_COVERED, PERSONAL_TRAVEL_NOT_COVERED or OUTSIDE_POLICY_SCOPE | request roles or NONE | POLICY_STATEMENT, PERSONAL_TRAVEL, APPENDIX_RECEIPTS, SCOPE or DEFINITIONS (26-28, 76-77, 164-170, 762-764) |
| `vetch-hollow` | refusal | REFUSE | PERSONAL_TRAVEL_NOT_COVERED or OUTSIDE_POLICY_SCOPE | request roles or NONE | PERSONAL_TRAVEL, POLICY_STATEMENT, SCOPE or DEFINITIONS (164-170) |
| `willow-crag` | flag | FLAG_FOR_APPROVAL (aircanada-economy, ECONOMY) | APPROVAL_REQUIRED or PRE_TRIP_REQUEST_REQUIRED | VICE_CHANCELLOR_BUSINESS_FINANCE | PRE_TRIP_APPROVAL, INTERNATIONAL_TRAVEL or DEFINITIONS (53-55, 151-153) |
| `yarrow-flint` | flag | FLAG_FOR_APPROVAL (southwest-economy, ECONOMY) | APPROVAL_REQUIRED or PRE_TRIP_REQUEST_REQUIRED | SUPERVISOR_APPROVER or FINANCIAL_APPROVER | BLANKET_AUTHORIZATION or PRE_TRIP_APPROVAL (177-181) |
| `zinnia-marsh` | flag | FLAG_FOR_APPROVAL (alaska-economy, ECONOMY) | UNCLEAR_POLICY_TEXT or APPROVAL_REQUIRED | NOT_NAMED, UNIVERSITY_TRAVEL_OFFICE, VC, SUPERVISOR_APPROVER or EXPORT_CONTROL_OFFICE | PRE_TRIP_APPROVAL (148-149, 153-154) |

"AIR_BOOKING etc." is AIR_BOOKING, COMMERCIAL_AIR, MOST_ECONOMICAL_RATES or PRE_TRIP_APPROVAL (plus
INTERNATIONAL_TRAVEL abroad); "request roles" are SUPERVISOR_APPROVER and FINANCIAL_APPROVER, whose approval of the
request is on file in every case.

Mix (EDGE_CASES.md 5.2, 24 row): 5 easy, 6 boundary twins, 4 multi-rule, 2 hidden clause, 2 distractor, 2 refusal,
3 flags (12.5%; the 15% cap is 3). Decisions: 19 BOOK (17 economy, 1 premium economy, 1 business), 2 REFUSE, 3
FLAG_FOR_APPROVAL. Twin pairs: a premium economy fare equal to the coach fare against one dollar over it
(`garnet-reed`, `heron-slate`; "not to exceed", inclusive); the cheapest connection landing 25 minutes before or after
the traveller's deadline at home (`iris-copper`, `juniper-wold`) and abroad, overnight (`kestrel-moor`,
`linden-shoal`).

Flags, each with clear twins on both sides:

- **"may require additional approval based on campus-specific procedures"** (lines 153-154): the policy defers
  non-continental US travel to procedures it does not give. `zinnia-marsh` (Honolulu, supervisor and financial
  approvals on file); twins `birch-lantern` (continental: book) and `dune-sparrow` (abroad, Vice Chancellor on file:
  book).
- **Approval required.** `willow-crag`: Toronto is International Travel (outside the US, passport needed), and the
  Vice Chancellor's approval is missing; twins `dune-sparrow` and `birch-lantern`. `yarrow-flint`: a blanket
  authorization for in-state visits does not cover a flight to Austin, so an individual request is needed; twins
  `birch-lantern` and `ember-thicket`.

Approvers follow the template's rule 4' (SYNC_NOTES.md): a booking accepts every sign-off on file it relies on (the
request's two approvals, the Vice Chancellor's abroad, the ADA/504 coordinator's accommodation) and `NONE`; a sign-off
on file that the decision does not use is accepted beside `NONE` (the refusals; `tansy-bluff`'s accommodation); a hold
accepts only the awaited roles. A booking that declines what the traveller asked for gives why in its reason (the task
instructions say so), so `LOWEST_FARE` is not accepted there.

**Duration.** The policy has no flight-length rule (no premium cabin for long flights at all), so
`rules.DURATION_RULES` is empty and `rules.over` raises. `handbook.json` `background_offers` is 0; each pinned search
sets its own number, and every twin, deadline, outside-fare and flag search has none.

Degenerate agents (`tests/test_verifier.py`): one that always holds the right offer as unclear passes 1 case
(`zinnia-marsh`); one that always books the cheapest seat with `LOWEST_FARE`, `NONE` and the right section passes 9
of 24, 37.5% (`birch-lantern`, `dune-sparrow`, `ember-thicket`, `fern-gable`, `iris-copper`, `kestrel-moor`,
`opal-fjord`, `sorrel-pike`, `tansy-bluff`).

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller, route, passport need, dates, purpose, latest useful landing, requested cabin and mode, outside fares, the travel request filed and the sign-offs on file | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date, as the university's agency lists them: the pinned scenario offers plus seeded background offers on those searches only; a search the case does not pin lists nothing and says so | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-nebraska-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this policy's scenario ids, approvers, sections, six reason
  codes (and decoys) and trip record.
- `src/plugin/`: `world.py`, `scenarios.py`, `guide.py`, `answer.py`, `tools.py` (shared), `rules.py` (this policy's
  rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of the shared modules and `rules.py`, plus `booking.py` and `tools.py`.
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this policy's settings.
- `tests/build_scenarios.py`: writes the scenario files (an authoring aid, not a test).
- `tests/BUILD_NOTES.md`: decisions taken during the build, the blind read and the acceptance outputs.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 ../_template/check_shared.py .
# from a NanoAgent checkout (read-only use):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/nebraska-flight-policy.tar.gz
# from this folder, with that checkout's Python:
/path/to/nanoagent/nanoagent/.venv/bin/python ../_template/tools/stock_verify.py .
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`).
