# Build notes: nebraska-flight-policy (wave 3, 2026-11-24)

Built to `pilot_work/tier_plan/build/WAVE3_BUILD_BRIEF.md` from the frozen handbook
`pilot_work/originals/nebraska/frozen/nebraska_policy.txt` (6,241 words, 806 lines, sha256 fe3ec93c...e5431d; under
10,000 words, so 24 scenarios). Made with `_template/instantiate.py nebraska-flight-policy --slug nebraska --task-id
book-nebraska-flight --currency USD --background 0 --scenarios 24`; `handbook.json` then got the raw PDF's sha256 and
`frozen_on`. The user was asleep; every choice below is the recommended one, taken without asking.

## Flight rules the handbook supports (frozen line numbers)

| Clause | Lines | Operator / kind | Used by |
|---|---|---|---|
| A Pre-Trip Request for each Travel Status instance | 136-141 | mandatory | yarrow-flint (its own request needed) |
| Supervisor Approver and Financial Approver approve it, before any booking | 143-146 | mandatory precondition | every case's record holds both approvals |
| Blanket Travel Authorization: city limits, 100-mile radius and/or State limits; other travel individually | 172-181 | mandatory | yarrow-flint |
| International / non-continental: "well-advised" to file 30 days ahead; "should" (450-452) | 148-151 | advice (soft) | sorrel-pike (distractor) |
| International Travel needs the Vice Chancellor of Business and Finance (or designee) | 151-153 | mandatory approver | dune-sparrow, kestrel-moor, linden-shoal, maple-cinder, nutmeg-ridge, sorrel-pike, willow-crag |
| International Travel defined: outside the US and territories, or a passport needed | 53-55 | definition | willow-crag (Canada), zinnia-marsh (Hawaii is not) |
| Non-continental US travel "may require additional approval based on campus-specific procedures" | 153-154 | unclear | zinnia-marsh |
| Private, chartered and State planes need the Vice Chancellor; other forms of travel need a request | 156-158, 316-321 | mandatory approver | opal-fjord |
| Most economical means that meet the approved goals of the trip | 160-162 | "should use their best efforts" | iris-copper, juniper-wold, kestrel-moor, linden-shoal |
| Personal travel: disclosed; only the business portion paid | 164-170 | payment rule | vetch-hollow |
| Commercial airlines expected | 208-211 | "expected" | opal-fjord |
| International flights through the contracted agency; outside only when the flights are not available there | 222-225 | mandatory ("only when") | maple-cinder |
| Domestic air outside the agency: proof of a comparable, less expensive fare with all fees, same day | 228-234 | mandatory ("must") | pewter-glen |
| Ticket not above the coach or main cabin price; explain a fare that is not the lowest listed | 237-239 | "not to exceed" (inclusive) | every booking; twins garnet-reed / heron-slate |
| Upgrades at the traveller's own cost, as an exchange with the agency | 241-247 | permission | nutmeg-ridge |
| Exemptions only with documentation such as an ADA plan, described to the Travel Office | 118-123 | mandatory | russet-dell, tansy-bluff (not used) |
| Non-University personnel (contracted speakers) follow the policy | 102-106 | "expected to comply" | quartz-bramble |
| University business only; spouse/companion expenses not reimbursable (appendix) | 26-28, 762-764 | mandatory | umber-loch |
| Airfare row of the appendix: tickets through the agency | 563-567 | mandatory | maple-cinder, pewter-glen |

Not tested, and why: the handbook has no flight-length threshold and no premium-cabin entitlement at all (so no
duration hook: `DURATION_RULES = ()`, `DURATION_CASES = []`), no advance-purchase rule for tickets, no connection or
routing rule, no preferred-carrier, refundable-fare, rail or drive-instead rule, no rule on several travellers booked
together (the `multi_traveller` overlay is not required) and no overnight-stop rule. Executive Memorandum No. 25 (line
455) is only a pointer to another document, so no scenario goes to a Level 3/4 country. The cancellation rule
(249-255) and the meal, lodging and expense-deadline rules appear only as distractors.

## Decisions taken (recommended choices)

1. **No Nebraska airport in the shared world.** OMA, LNK and the regional airports (GRI, EAR, LBF, BFF) are missing.
   Travellers are based at the university's western Nebraska and Kearney locations (Panhandle and West Central
   research and extension centers, UNK, the Kearney extension office), whose staff plausibly drive to Denver; most
   trips leave from DEN, and the record's `campus` says "drives to Denver to fly". A speaker flies SEA to DEN and a
   companion-free personal leg starts in Chicago. See the template change request below.
2. **What search_flights lists.** The offers are the university-contracted agency's fares (the task's
   `search_flights` description says so). A traveller's outside fare is a trip-record fact (`outside_fares`,
   `wants_to_book_outside`). Only the cases where the outside purchase is not allowed are modelled (the agency then
   books); a qualifying outside purchase would make the traveller the buyer, which none of BOOK/REFUSE/FLAG describes,
   so `rules.outside` raises on it and no scenario uses it.
3. **Approvals.** Every record holds the request's Supervisor Approver and Financial Approver approvals (lines
   143-146). International trips also need the Vice Chancellor's (`TRAVEL_ABROAD` sign-off). Approver accept sets
   follow SYNC_NOTES 4': bookings accept the roles relied on and NONE; refusals accept the unused request roles and
   NONE (4(b)); `tansy-bluff` also accepts the unused ADA coordinator; holds accept only the awaited roles
   (willow-crag: the Vice Chancellor; yarrow-flint: supervisor or financial approver; zinnia-marsh: NOT_NAMED, the
   University Travel Office, named at 148-149 among the reviewers, or the Vice Chancellor by analogy with 151-153).
4. **The 30-day advice is soft.** "Well-advised" and "should" (148-151, 450-452) protect the approvals; once they are
   on file a late filing changes nothing (`sorrel-pike`). It is never a refusal.
5. **The coach cap compares prices, not cabins** (237-238: "a ticket not to exceed the price of the coach or main cabin
   rate"). A premium economy fare equal to the lowest coach fare (also the lowest listed price) is allowed when asked
   for (`garnet-reed`, key: premium economy only, since the request decides); one dollar over is not (`heron-slate`).
   "Coach rate" is the lowest coach fare that meets the trip's goals; every twin makes that the same flight's coach
   fare, so the reading "same flight" or "lowest anywhere" never matters.
6. **Deadlines.** Lesson 4: an answer that depends on landing time has a `must_arrive_by` in the record and the same
   words in both twins' requests. The most economical flight that lands in time is booked (160-162), and the deadline
   is the "brief explanation" of 238-239. Reasons: LOWEST_FARE (it is the lowest fare that meets the goals) or
   ARRIVAL_NEEDED_FOR_BUSINESS. Every other case states when the business starts (next morning, a later date) so
   arrival never matters.
7. **Self-paid upgrades** (`nutmeg-ridge`). The university buys the coach ticket; the traveller exchanges it with the
   agency and pays (241-244). Key: the lowest coach fare only.
8. **Charter** (`opal-fjord`). No Vice Chancellor approval for the charter is on file (156-158), commercial airlines
   are expected (208-211), and the request's fallback is a regular flight: BOOK the lowest coach fare,
   PRIVATE_AIRCRAFT_NOT_APPROVED (a handbook code here, though other plugins carry it as a decoy).
9. **Reason codes.** Handbook codes: PRIVATE_AIRCRAFT_NOT_APPROVED, TRAVEL_AGENCY_REQUIRED,
   OUTSIDE_FARE_COMPARISON_NOT_MET, PRE_TRIP_REQUEST_REQUIRED, POLICY_EXEMPTION_DOCUMENTED, ARRIVAL_NEEDED_FOR_BUSINESS.
   Decoys (subjects grepped in the frozen text, none present): WEEKEND_TRAVEL_HOME, WEEKEND_TRIP_NOT_EARNED,
   NEXT_OF_KIN_TRAVEL, FLY_AMERICA_US_CARRIER_REQUIRED, OPEN_SKIES_AGREEMENT, CREATIVE_TICKETING,
   DENIED_BOARDING_NOT_ALLOWED, DOUBLE_BOOKING_PROHIBITED, SAME_CLASS_AS_CUSTOMER, CANDIDATE_TRIP_NOT_COVERED. Dropped:
   CHANCELLOR_WRITTEN_AUTHORIZATION (a reader could use it for the Vice Chancellor's approval), EXTENDED_TRAVEL_SAVINGS
   ("extended travel" appears in the meal rules), TRAVEL_PACKAGE_NOT_ITEMIZED ("itemized" receipts appear).
10. **Declined requests (lesson 12).** cobalt-meadow, heron-slate, quartz-bramble (business or premium declined):
    UPGRADE_NOT_ELIGIBLE only; nutmeg-ridge: TRAVELER_PAYS_UPGRADE or UPGRADE_NOT_ELIGIBLE; opal-fjord:
    PRIVATE_AIRCRAFT_NOT_APPROVED; maple-cinder: TRAVEL_AGENCY_REQUIRED; pewter-glen: OUTSIDE_FARE_COMPARISON_NOT_MET or
    TRAVEL_AGENCY_REQUIRED. None accepts LOWEST_FARE: the ground for declining is the coach cap, the upgrade rule, the
    plane rule or the agency rule, not the lowest-fare rule.
11. **One ticket per case.** Every case is one way; `return_date` is empty everywhere.
12. **Background offers.** `background_offers` 0; the plain cases set 2 per search; every twin, deadline, outside-fare
    and flag search sets 0, so twins differ only in their one fact (flight numbers and offer ids aside).
13. **Degenerate baselines.** Always-flag passes 1 (zinnia-marsh). Always-cheapest (LOWEST_FARE, NONE) passes 8:
    birch-lantern, dune-sparrow, ember-thicket, fern-gable, iris-copper, kestrel-moor, sorrel-pike, tansy-bluff.
    `MAX_PASS_ALWAYS_FLAG = 1`, `MAX_PASS_ALWAYS_LOWEST = 8`.

Mix: 5 easy, 6 boundary twins, 4 multi-rule, 2 hidden clause, 2 distractor, 2 refusal, 3 flag; decisions 19 BOOK, 2
REFUSE, 3 FLAG. Overlays: multi_leg 5, date_arithmetic 4, month_end 2, personal_travel 2, dearer_option 3,
upgrade_not_taken 2, outside_air_section 8.

## Hosted-cap estimate

0.2 tokens a character of policy plus 1,800 (Thornton/NJC paid calibration): 42,108 characters, so call 1 about 10,200
input tokens, call 2 about 11,000 (the trip record here is longer than most: request, sign-offs, outside fares), call 3
11,500-12,500 (2 to 8 offers). A 3-call run is about 33,000-34,500 input tokens, about 48,000 with the final message
and output: under the 65,536 hosted cap with about 17,000 to spare (one extra tool call fits).

## Blind read (non-flag scenarios), from the handbook text and the tool outputs only

I dumped `get_trip` and the pinned `search_flights` output of every case (background offers included) and re-derived
each answer from the frozen text, without looking at `rules.py`.

| Scenario | My reading | Agrees |
|---|---|---|
| birch-lantern | request approved (143-145); workshop next morning; cheapest coach DL 09:45 $214 (237-239) | yes |
| cobalt-meadow | business exceeds the coach price (237-238); fallback economy: B6 07:00 $289 | yes |
| dune-sparrow | England: International (53-55); VC approval on file (151-153); cheapest coach BA $742 | yes |
| ember-thicket | AS $168 sold out; cheapest buyable coach UA 09:20 $184 | yes |
| fern-gable | connection welcome, conference next morning: UA via ORD $219 | yes |
| garnet-reed | PE $264 equals the lowest coach $264: does not exceed it; asked for: book PE 08:05 | yes (two-reader risk: a reader may book the equal-price coach seat) |
| heron-slate | PE $265 exceeds coach $264: book coach UA 08:05 $264 | yes |
| iris-copper | DL via MSP lands 16:35, by 17:00: cheapest $254 | yes |
| juniper-wold | DL lands 17:25, late; cheapest in time B6 10:40 $342 (lands 16:35); UA $389 dearer | yes |
| kestrel-moor | UA via IAD lands 08:45 on the 9th, by 10:00; VC on file: $812 | yes |
| linden-shoal | UA lands 11:15, late; LH nonstop lands 08:50: $1,046 | yes |
| maple-cinder | international: outside the agency only if the flight is not available there (222-225); agency lists AF 2168: book it, $734 | yes |
| nutmeg-ridge | ticket capped at coach; upgrade is the traveller's exchange (241-244): cheapest coach NH $1,095 | yes (two-reader risk: a reader may book business with the traveller repaying) |
| opal-fjord | charter needs the VC (156-158), none on file; fallback airline: UA $176 | yes (risk: a reader may hold for the VC's charter approval despite the fallback) |
| pewter-glen | outside fare found Nov 28, today Dec 1: not same day (233-234); agency WN $186 | yes |
| quartz-bramble | contracted speaker follows the policy (103-106); business exceeds coach; AS $172 | yes |
| russet-dell | ADA plan, coordinator's description to the Travel Office, request incorporates it (118-123): cheapest business UA 12:40 $575 | yes |
| sorrel-pike | filed 19 days ahead (advice only); all approvals incl. VC on file: KL $864 | yes |
| tansy-bluff | asks economy despite the accommodation: AA 06:15 $169 | yes |
| umber-loch | spouse: not University business; appendix: companion expenses not reimbursable: REFUSE | yes |
| vetch-hollow | personal weekend leg: only business portion paid (164-170): REFUSE | yes |

All 21 non-flag scenarios agree. The flags were also re-read: willow-crag (Canada needs a passport and is outside the
US; VC missing: hold), yarrow-flint (out-of-state flight outside the blanket authorization's scope: hold for the
individual request's approvals), zinnia-marsh (Hawaii: not International, but "may require additional approval based
on campus-specific procedures" with no procedure given: unclear hold; both readings use the same lowest coach fare).

## Template change requests

1. **Add Nebraska airports to the shared world** (`world.py` `AIRPORTS`; no new hubs, so no existing route's offers
   move): OMA Eppley Airfield, Omaha (41.3032, -95.8941, UTC-360) and LNK Lincoln Airport (40.8510, -96.7592,
   UTC-360); optionally GRI Grand Island (40.9675, -98.3096) and EAR Kearney (40.7270, -99.0068). With them this
   plugin's trips could start from Omaha and Lincoln (UNO, UNMC, UNL) instead of a drive to Denver. Run
   `tools/world_diff.py` before syncing.
2. Observation, not blocking: the shared answer format has no way to say "the traveller buys it themselves and is
   reimbursed", so a handbook's qualifying outside-purchase path (Nebraska 228-234) cannot be a scenario.

## Acceptance outputs (final)

```
$ uv run pytest -q
196 passed, 3 skipped in 2.46s
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages in 8ms
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .  (stock checkout)
exit 0
$ nanoagent plugin pack . <scratchpad>/nebraska-flight-policy.tar.gz  (stock checkout)
packed . into <scratchpad>/nebraska-flight-policy.tar.gz (171347 bytes)
$ python ../_template/tools/stock_verify.py .  (stock checkout Python)
birch-lantern        right=True score=1.00 identical=True wrong-decision-rejected=True
cobalt-meadow        right=True score=1.00 identical=True wrong-decision-rejected=True
dune-sparrow         right=True score=1.00 identical=True wrong-decision-rejected=True
ember-thicket        right=True score=1.00 identical=True wrong-decision-rejected=True
fern-gable           right=True score=1.00 identical=True wrong-decision-rejected=True
garnet-reed          right=True score=1.00 identical=True wrong-decision-rejected=True
heron-slate          right=True score=1.00 identical=True wrong-decision-rejected=True
iris-copper          right=True score=1.00 identical=True wrong-decision-rejected=True
juniper-wold         right=True score=1.00 identical=True wrong-decision-rejected=True
kestrel-moor         right=True score=1.00 identical=True wrong-decision-rejected=True
linden-shoal         right=True score=1.00 identical=True wrong-decision-rejected=True
maple-cinder         right=True score=1.00 identical=True wrong-decision-rejected=True
nutmeg-ridge         right=True score=1.00 identical=True wrong-decision-rejected=True
opal-fjord           right=True score=1.00 identical=True wrong-decision-rejected=True
pewter-glen          right=True score=1.00 identical=True wrong-decision-rejected=True
quartz-bramble       right=True score=1.00 identical=True wrong-decision-rejected=True
russet-dell          right=True score=1.00 identical=True wrong-decision-rejected=True
sorrel-pike          right=True score=1.00 identical=True wrong-decision-rejected=True
tansy-bluff          right=True score=1.00 identical=True wrong-decision-rejected=True
umber-loch           right=True score=1.00 identical=True wrong-decision-rejected=True
vetch-hollow         right=True score=1.00 identical=True wrong-decision-rejected=True
willow-crag          right=True score=1.00 identical=True wrong-decision-rejected=True
yarrow-flint         right=True score=1.00 identical=True wrong-decision-rejected=True
zinnia-marsh         right=True score=1.00 identical=True wrong-decision-rejected=True
24 scenarios, 0 failures
```
