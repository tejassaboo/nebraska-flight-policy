# Independent audit: nebraska-flight-policy (2026-11-25)

Audited the builder's commit 773474f against `pilot_work/tier_plan/build/WAVE3_AUDIT_BRIEF.md`, the wave 3 build
brief's 12 lessons, MASTER_PLAN section 4, EDGE_CASES 1-3 and 5 and the worked audits (fedex-office,
goodman-networks, hillrom, georgia-sao). No money spent, nothing pushed. Line numbers are lines of the frozen
handbook (`src/plugin/data/policy.txt`).

## Method

I printed every scenario's `get_trip` output and pinned `search_flights` result through the plugin's own tools,
read the handbook's flight sections myself (definitions 45-77, exemptions 108-132, pre-travel 135-181, commercial
air, booking, upgrades and cancellations 207-255, other forms of travel 315-321, international 449-454, Appendix A
airfare and spouse rows), and answered each case before comparing with the key.

## Verdict

**Pass after fixes.** My decision and offer agree with the key on all 24 cases. The defects were in accept sets
(reasons, clauses, approvers) and one request's wording, not in any answer, so no world and no id changed.

- Flags: `willow-crag` (Toronto needs a passport, 53-55; the Vice Chancellor's approval, 151-153, is missing) and
  `yarrow-flint` (an Austin flight is outside the blanket authorization's in-state scope, 177-181, so an individual
  request with both approvals is needed first) are clear holds. `zinnia-marsh` is genuinely open: Hawaii is not
  International Travel, but "may require additional approval based on campus-specific procedures" (153-154) gives
  no procedure. Both readings (book now, or hold) use the same lowest fare, Alaska $396, the only held offer.
- Twins differ in one fact: `garnet-reed`/`heron-slate` (premium economy $264 or $265 against coach $264),
  `iris-copper`/`juniper-wold` (the Delta connection lands 16:35 or 17:25 against a 17:00 deadline),
  `kestrel-moor`/`linden-shoal` (the United connection lands 08:45 or 11:15 against 10:00).
- Requests leak no rule wording. "Pre-trip request", "blanket travel authorization" and "accommodation plan" are the
  names of the traveller's own forms, not rules. Every request that asks for something the policy declines has a
  fallback. Every case that depends on landing time has a stated deadline (`must_arrive_by` plus the same words in
  both twins). Every other case puts the business on a later day or the next morning.
- The decline-reason sentence is the last line of the task instructions in `nanoagent.yaml`.

## The builder's unsure list, settled

- **`garnet-reed`: book premium economy only, not coach.** Lines 237-238 cap the *price* ("a ticket not to exceed
  the price of the coach or main cabin rate"), not the cabin. The $264 premium economy fare equals the coach fare, and
  it is also the lowest listed price, so 238-239 asks for no explanation. The traveller asks for premium economy "if
  the university will pay for it". The university pays $264 either way, so the request decides (EDGE_CASES 3.17). A
  careful reader books premium economy. Coach at the same price refuses a request the text allows, which is the
  standex `juniper-flint` and uiowa `flint-harrow` precedent. A reader who calls premium economy an "upgrade" under
  241-244 still finds a $0 upgrade, which needs no exchange. Kept PE only. Added UPGRADE_WITHIN_FARE_MARGIN, and
  MOST_ECONOMICAL_RATES beside the accepted LOWEST_FARE.
- **`nutmeg-ridge`: coach only.** Line 237 caps the ticket the University buys at the coach price "at the time of
  purchase". Lines 241-244 give the only way to upgrade: the traveller "can contact the University-contracted travel
  management company, arrange the ticket exchange and pay for all fees associated with the upgrade". The text has no
  "the University buys business and the traveller repays" path. A business ticket bought now would exceed the cap at
  purchase. Lines 212-213 ("up to the total cost of the most economical option") are about alternative modes of
  travel, not cabins. The key stays the lowest coach fare (ANA $1,095); the traveller then upgrades it himself.
- **`opal-fjord`: BOOK commercial, no hold.**
  - The charter needs the Vice Chancellor's approval (156-158), which is not on file.
  - A charter also needs a request "affirming that no other, more economical means of travel is available"
    (316-318). That cannot be affirmed with a $176 airline fare listed.
  - search_flights lists no charter, so a hold could only hold a commercial offer. A commercial offer needs no sign-off
    beyond the approved request.
  - The traveller says "If a charter isn't possible, put me on a regular airline flight".
  - BOOK is the only defensible answer. FLAG stays rejected.
- **`zinnia-marsh` approver set: widened.** Lines 148-149 name the reviewers of "International and non-continental
  United States travel": "supervisors, export control offices, the University Travel Office and other University
  administration". The builder accepted the Travel Office from that sentence. The same sentence names supervisors and
  export control offices, so SUPERVISOR_APPROVER and EXPORT_CONTROL_OFFICE are now accepted too. NOT_NAMED (for "other
  University administration" and the unnamed campus procedure) and the Vice Chancellor (by analogy with 151-153) stay.
  The always-flag agent uses NOT_NAMED and still passes 1.

## DEN as the origin

The shared world has no OMA, LNK or regional Nebraska airport, so every Nebraska-based traveller flies from DEN. This
reads naturally:

- The trip record's `campus` says "(drives to Denver to fly)".
- Most travellers are at the Panhandle center in Scottsbluff, about three hours from Denver.
- `birch-lantern`'s request says "I'm driving down to Denver".
- The others say "Denver to X", as a traveller who always flies from DEN would.
- The UNK and Kearney travellers (`cobalt-meadow`, `russet-dell`, `yarrow-flint`) are the least natural, since Omaha
  is nearer. Their record still states the drive, and no answer depends on the origin.
- `yarrow-flint`'s blanket authorization covers Nebraska only, and the flight leaves from Colorado to Texas. That
  agrees with the hold: either fact puts the trip outside the authorization.

Kept as built. The template change request for OMA/LNK stands.

## Defects found and fixed

| # | Scenario | Problem | Fix |
|---|---|---|---|
| 1 | `pewter-glen` | The request said the Expedia fare found on November 28 was "less than the agency charges". A reader could take the comparison as made that day (the same day, as 233-234 asks), call the outside purchase allowed and buy nothing. The format cannot express that answer. | Request now reads "less than the agency is charging today": the two prices are from different days, so the same-day test plainly fails. The key is unchanged (agency WN $186). |
| 2 | `opal-fjord` | Lines 316-318 make the charter wait on an affirmation that no more economical means exists, and 212-213 pay only up to the most economical option. Declining the charter on that economy ground is defensible, and lesson 12 allows LOWEST_FARE when the lowest-fare rule is itself a ground for declining. | Accept LOWEST_FARE beside PRIVATE_AIRCRAFT_NOT_APPROVED, and the clause MOST_ECONOMICAL_RATES. |
| 3 | `cobalt-meadow`, `heron-slate`, `quartz-bramble` | The decline of business or premium economy is accepted under UPGRADES (241-244), whose rule is that an upgrade is the traveller's own. TRAVELER_PAYS_UPGRADE was not accepted with it. This follows the georgia-sao `azalea-crest` and `magnolia-bluff` fix. | Accept TRAVELER_PAYS_UPGRADE beside UPGRADE_NOT_ELIGIBLE. |
| 4 | `garnet-reed` | Granting premium economy because its fare is within the coach fare has a specific code. | Accept UPGRADE_WITHIN_FARE_MARGIN, and MOST_ECONOMICAL_RATES beside LOWEST_FARE. |
| 5 | `russet-dell` | Only COMPLIANCE_AND_EXEMPTIONS was accepted. Line 162 counts "special needs" in the most economic option. The approved pre-trip request incorporates the accommodation (122-123, 143-146), and its approvers are accepted. | Accept MOST_ECONOMICAL_RATES and PRE_TRIP_APPROVAL. |
| 6 | `umber-loch`, `vetch-hollow` | The definitions (Traveler, 76-77: an employee "traveling on approved University business"; Travel Status, 71-73) are a natural section for "not University business". | Accept DEFINITIONS. |
| 7 | `zinnia-marsh` | The approver set was narrower than the sentence it relied on (see above). | Accept SUPERVISOR_APPROVER and EXPORT_CONTROL_OFFICE. |

Considered and not added:

- APPROVAL_REQUIRED on `opal-fjord`. It is the hold code. PRIVATE_AIRCRAFT_NOT_APPROVED names the same ground
  specifically.
- OUTSIDE_FARE_COMPARISON_NOT_MET on `maple-cinder`. The international rule (222-225) asks whether the flight is
  available through the agency, not for a comparison.
- Coach on `garnet-reed` (see above).

`MAX_PASS_ALWAYS_LOWEST`: **8 -> 9** (37.5%, under the ~40% bar): `opal-fjord` joins `birch-lantern`, `dune-sparrow`,
`ember-thicket`, `fern-gable`, `iris-copper`, `kestrel-moor`, `sorrel-pike` and `tansy-bluff`. The count was confirmed
by running the degenerate agent through the verifier (`tests/test_verifier.py`). `MAX_PASS_ALWAYS_FLAG` stays 1.

## Seen and kept

- `sorrel-pike`: the request was filed 19 days ahead. Lines 148-151 and 450-452 are advice ("well-advised",
  "should"), and every approval, including the Vice Chancellor's, is on file. BOOK.
- `maple-cinder`: the agency lists AF 2168 at $734, so the international outside-purchase exception does not apply.
  BOOK the agency fare.
- `russet-dell`: the cheaper business fare is UA 12:40 ($575), not 07:15 ($612). The meeting is the next morning.
- `tansy-bluff`: the traveller declines the accommodated cabin, so BOOK the lowest coach fare. The unused ADA
  coordinator is accepted beside NONE (4(b)).
- `zinnia-marsh` stays a FLAG-only key, as for every unclear-text flag in the template. Full-arm models often take one
  reading of an unclear phrase without flagging it, so expect slips there, not defects.

## Files changed

- `src/plugin/rules.py` and `verifier/rules.py` (byte-identical): the accept sets above.
- `tests/build_scenarios.py`: the `pewter-glen` request and the accept sets. 10 scenario JSON files were
  regenerated.
- `tests/plugin_spec.py`: `MAX_PASS_ALWAYS_LOWEST = 9`.
- `README.md`: the scenario table rows and the degenerate-agent paragraph.

## Check outputs (audit commit)

- `uv run pytest -q`: 196 passed, 3 skipped (the empty duration parameter sets).
- `uv run ruff check .`: all checks passed.
- `uv lock --check`: ok.
- `python3 ../_template/check_shared.py .`: ok.
- stock `tools/stock_verify.py .`: 24 scenarios, 0 failures.
- stock `nanoagent plugin inspect .`: exit 0.
