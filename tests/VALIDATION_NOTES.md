# Validation notes: nebraska-flight-policy (paid wave 3 validation, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w3_2026-11-25/nebraska-flight-policy@w3/`, arm
`full`, DeepSeek V4 Flash (Nebius fp8), temperature 0, max_steps 6, max_tokens 8192, one run per scenario, at plugin
head 89da9cf. Line numbers are lines of `src/plugin/data/policy.txt`.

## Results

19/24 valid (79.2%), mean field score 0.896, **easy 4/5** (cobalt-meadow fails). By category: boundary 5/6,
distractor 2/2, easy 4/5, flag 1/3, hidden 2/2, multi 3/4, refusal 2/2. $0.00150 billed per run, 3.9 calls per run,
12,618 prompt tokens per call; no run would exceed the hosted 65,536 cap. Every run submitted.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| cobalt-meadow | **easy** | right offer (JetBlue $289), cabin and approver; reason LOWEST_FARE, clause MOST_ECONOMICAL_RATES; key UPGRADE_NOT_ELIGIBLE or TRAVELER_PAYS_UPGRADE, AIR_BOOKING or UPGRADES | model slip | It found the ground and named it: "The university policy (Air Booking / Upgrades) only pays for coach/main cabin rates ... So business class is not eligible". Then it picked the generic code and a clause by name: "Reason code LOWEST_FARE ... Clause could be MOST_ECONOMICAL_RATES". The task's last line asks for the reason the request is declined. The ground is line 237's coach-price cap, not a lowest-fare rule: garnet-reed books premium economy above the lowest coach seat on the same cap. Lines 159-162 state a general economy aim, not the cap. The sibling decline quartz-bramble answered UPGRADE_NOT_ELIGIBLE / UPGRADES and passed. Accepting LOWEST_FARE would also lift the always-cheapest agent to 10/24 (41.7%). Not loosened. |
| heron-slate | boundary_twin | premium economy LK6U-E8XJ ($265), PREMIUM_ECONOMY_ALLOWED; key coach JK8X-3L6F ($264) | model slip (limit rationalised away) | "$265 vs economy $264. That's essentially the same price (only $1 more) ... Premium economy at $265 is essentially the coach rate." Line 237 says "not to exceed the price of the coach or main cabin rate". One dollar over is the designed boundary; the twin garnet-reed ($264) passed with premium economy. |
| nutmeg-ridge | multi_rule | ANA business HMR4-T3M2 ($4,980), TRAVELER_PAYS_UPGRADE, UPGRADES; key ANA economy 6D5Z-QV2T ($1,095) | model slip (borderline) | It quoted line 237 ("should book a ticket not to exceed the price of coach") and then went on to "If the Traveler purchases a ticket that is not the lowest listed price, a brief explanation ... must be provided", and booked business on the University's ticket. Lines 241-244 give the only upgrade path: the traveller "can contact the ... travel management company, arrange the ticket exchange and pay for all fees". The University buys coach, and the traveller upgrades it. The audit settled this case the same way (AUDIT_NOTES, "nutmeg-ridge: coach only"). The reason code it gave is accepted; only the offer and cabin are wrong. If a re-run books business again, the lead may weigh the FedEx mallow-pier precedent. That precedent rests on FedEx line 147, which pays from the coach fare, and Nebraska has no such sentence. |
| willow-crag | flag | BOOK Air Canada $318 (the held offer), LOWEST_FARE, NONE; key FLAG for VICE_CHANCELLOR_BUSINESS_FINANCE | model slip | "This is international travel (Canada requires passport) ... Export control review completed ... no further approval is needed." It never read lines 151-153 ("International Travel will require additional approval from the Traveler's respective Vice Chancellor of Business and Finance"). The record has only the supervisor and financial approvals. It is a clear hold. |
| zinnia-marsh | flag | BOOK Alaska $396 (the held offer), LOWEST_FARE; key FLAG | model slip | "The pre-trip request was approved by supervisor and financial approver. No issues." It never weighed lines 153-154 ("Non-continental United States travel may require additional approval based on campus-specific procedures"). The audit judged this text genuinely open. This is the usual one-reading-taken-as-settled flag failure, except that here the model did not take up either reading. The key stays FLAG-only, as for every unclear-text flag in the template. |

## Fixes

None. All five failures are slips, and no accept set, record or request changed.

## Q2

The always-cheapest agent passes **9/24 (37.5%)** before and after (`MAX_PASS_ALWAYS_LOWEST = 9`, unchanged). It
fails cobalt-meadow (LOWEST_FARE on a declined business request).

## Re-score

Stored answers graded against this head: **19/24, easy 4/5** (unchanged).

## Re-run

Required: **cobalt-meadow**. Its record did not change, but it is the easy case and must come back valid. It is a
slip, and nothing was changed to make it pass. Optional: nutmeg-ridge (a borderline slip on a self-paid upgrade) and
zinnia-marsh (open text; if it books again, the lead may weigh a BOOK under a new id).

## Checks

`uv run pytest -q` (196 passed, 3 skipped), `uv run ruff check .`, `uv lock --check`, `check_shared.py`, `tools/stock_verify.py` (24
scenarios, 0 failures), stock `nanoagent plugin inspect .` (exit 0).
