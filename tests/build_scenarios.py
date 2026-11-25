"""Writes the University of Nebraska scenario JSON files (an authoring aid, not a test; the JSON files are the
truth).

    uv run python tests/build_scenarios.py

Flight numbers that a trip record refers to (an outside fare's flight) are read from the shared world, so they
match what search_flights lists. Expected answers are hand-written here; tests/test_scenarios.py checks them
against rules.solve.

The shared world has no Nebraska airport (OMA, LNK and the regional airports are missing; see BUILD_NOTES.md,
template change requests), so the travellers are based at western Nebraska and Kearney locations and drive to
Denver International, the origin of most trips.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

from plugin.world import pinned_offers

POLICY = (ROOT / "src/plugin/data/policy.txt").read_text(encoding="utf-8").split("\n")
OUT = ROOT / "src/plugin/data/scenarios"


def norm(text):
    return " ".join(text.split())


def keep(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    quote = text if quote is None else quote
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "sha256": hashlib.sha256(text.encode()).hexdigest(), "quote": quote, "why": why}


def aside(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "quote": quote, "why": why}


# ----- clauses the answers rest on -----
REQUEST = keep(143, 145, "All Pre-Trip Requests will require approval by the Traveler's Supervisor Approver and "
               "Financial Approver for all funding sources. Pre-Trip Requests are required prior to any bookings",
               "the request, approved by the supervisor and financial approvers, comes before any booking")
EACH_TRIP = keep(136, 137, "All Travelers are required to submit a Pre-Trip Request prior to each separate Travel "
                 "Status instance.", "a request for each trip")
COACH_CAP = keep(237, 239, None, "a ticket not above the coach or main cabin price; a brief explanation for a ticket "
                 "that is not the lowest listed price")
ECONOMICAL = keep(160, 162, None, "the most economical means of travel that meet the approved goals of the trip")
COMMERCIAL = keep(208, 211, None, "commercial airlines are expected")
INTL_DEFINED = keep(53, 55, None, "International Travel: outside the US and its territories, or a destination that "
                    "needs a passport")
INTL_VC = keep(151, 153, "International Travel will require additional approval from the Traveler's respective Vice "
               "Chancellor of Business and Finance or their designee(s).",
               "travel abroad also needs the Vice Chancellor's approval")
NON_CONTINENTAL = keep(153, 154, "Non-continental United States travel may require additional approval based on "
                       "campus-specific procedures.", "non-continental US travel: an approval the handbook leaves to "
                       "campus procedures")
PLANES = keep(156, 158, None, "privately owned, chartered and State planes need the Vice Chancellor's approval")
OTHER_FORMS = keep(316, 321, None, "a chartered plane needs a request showing no more economical means and a review")
PERSONAL = keep(164, 170, None, "personal travel in Travel Status: only the business portion is paid")
POLICY_STATEMENT = keep(26, 28, None, "the University pays for travel in the performance of University business")
SPOUSE_ROW = keep(762, 764, None, "appendix: spouse/companion expenses are not reimbursable")
BLANKET = keep(177, 181, None, "a blanket authorization covers travel within city limits, a 100-mile radius or the "
               "state; other travel goes through the individual request")
INTL_AGENCY = keep(222, 225, None, "international flights through the contracted agency; outside it only when the "
                   "required flights are not available there")
OUTSIDE_DOMESTIC = keep(228, 234, None, "domestic air outside the agency needs a same-day proof of a comparable, less "
                        "expensive fare with all fees")
APPENDIX_AIR = keep(563, 567, None, "appendix: airline tickets through the agency; other sources need review")
UPGRADES = keep(242, 244, None, "an upgrade is the traveller's own, arranged as an exchange with the agency")
NON_UNIVERSITY = keep(103, 106, None, "people doing business with the University, speakers included, follow the policy")
EXEMPTION = keep(118, 123, None, "exemptions only with documentation such as an ADA accommodation plan, described to "
                 "the University Travel Office")

# ----- nearby clauses that must not change the answer -----
THIRTY_DAYS = aside(148, 151, "Travelers are well-advised to submit Pre-Trip Requests for International and "
                    "non-continental United States travel no less than thirty (30) days in advance of travel.",
                    "advice on when to file the request; the approvals are already on file")
THIRTY_AGAIN = aside(450, 452, "Pre-Trip Requests for international destinations should be submitted for approval at "
                     "least thirty (30) days in advance of departure.", "the same advice, in the international section")
CANCEL = aside(253, 255, "The cost of a cancelled ticket purchased outside of the University-contracted travel "
               "management company will be the sole responsibility of the Traveler",
               "a cancellation rule; nothing is cancelled")
MEALS = aside(372, 372, "Breakfast Departure time is at or before 6:30 a.m.", "a meal allowance, not a fare rule")
DEADLINE = aside(402, 402, "All travel expenses must be submitted within 60 days after the last day of travel.",
                 "a claim deadline, not a booking rule")
PCARD = aside(201, 202, "The University-issued purchasing card (known as a \"P-card\") is available only for pre-paid "
              "conference registrations.", "how a cost is paid, not which ticket")
BTA_RADIUS = aside(177, 179, "A BTA can consist of any combination of travel within city limits, a 100-mile radius of "
                   "the Traveler's respective campus", "only for blanket authorizations; this trip has its own request")
INSURANCE = aside(473, 475, "No pre-trip reporting or enrollment is required for insurance coverage.",
                  "insurance needs no filing; it does not replace the approvals")
DIRECT_PAY = aside(189, 190, "The University has the ability to pay directly for approved travel expenses for airfare",
                   "the University may pay the agency directly; not a fare rule")
LODGING_COMPANION = aside(342, 345, "Only the single occupancy rate plus taxes and fees, if applicable, will be covered by the University when the Traveler shares a room with a non-University companion(s).", "a lodging rule for a shared room")

# ----- builders -----


def trip(**fields):
    base = {
        "traveller_name": "", "traveller_title": "", "passenger": "EMPLOYEE", "accompanies": "",
        "campus": "UNL Panhandle Research, Extension and Education Center, Scottsbluff (drives to Denver to fly)",
        "origin": "DEN", "destination": "", "destination_needs_passport": False, "travel_date": "",
        "return_date": "", "booking_date": "", "purpose": "", "purpose_kind": "CONFERENCE", "must_arrive_by": "",
        "requested_cabin": "ECONOMY", "traveller_pays_upgrade": False, "requested_mode": "AIRLINE",
        "wants_to_book_outside": False, "outside_fares": [], "trip_request": None, "sign_offs": None,
    }
    unknown = set(fields) - set(base)
    assert not unknown, unknown
    base.update(fields)
    assert base["trip_request"] and base["sign_offs"] is not None
    return base


def request(kind, submitted, covers):
    return {"kind": kind, "submitted_on": submitted, "covers": covers}


def sign(role, name, subject, covers, given):
    return {"role": role, "name": name, "subject": subject, "covers": covers, "given_on": given}


def approvals(supervisor, financial, given, covers="The trip request, approved"):
    return [sign("SUPERVISOR_APPROVER", supervisor, "TRIP_REQUEST", covers, given),
            sign("FINANCIAL_APPROVER", financial, "TRIP_REQUEST", covers + "; the funding is budgeted", given)]


def abroad(name, given, covers="Approval of the travel abroad for this trip"):
    return sign("VICE_CHANCELLOR_BUSINESS_FINANCE", name, "TRAVEL_ABROAD", covers, given)


def offer(slot, flight, cabin, cents, seats=True):
    data = {"slot": slot, "flight": flight, "cabin": cabin, "fare_cents": cents}
    if not seats:
        data["seats"] = False
    return data


def expected(decision, slots, cabins, reasons, approvers, clauses, phrase=""):
    return {"decision": decision, "offer_slots": slots, "cabins": cabins, "reason_codes": sorted(reasons),
            "approvers": sorted(approvers), "clauses": sorted(clauses), "unclear_phrase": phrase}


def search(origin, destination, date, flights, offers, background=2, name="main"):
    return {"name": name, "origin": origin, "destination": destination, "date": date, "return_date": "",
            "background": background, "flights": flights, "offers": offers}


def first_flight(scenario_id, search_spec, slot):
    for name, made in pinned_offers(scenario_id, search_spec):
        if name == slot:
            return made.segments[0].flight_number
    raise KeyError(slot)


S = []


def scenario(id, category, overlays, request_text, trip_, searches, exp, must_keep, notes, twin_of="", twin_fact="",
             flag_twins=(), ambiguity="none", distractors=()):
    if isinstance(searches, dict):
        searches = [searches]
    S.append({
        "id": id, "category": category, "overlays": list(overlays), "twin_of": twin_of, "twin_fact": twin_fact,
        "flag_twins": list(flag_twins), "ambiguity_note": ambiguity, "request": request_text, "trip": trip_,
        "world": {"searches": searches}, "expected": exp, "must_keep": list(must_keep),
        "distractors": list(distractors), "design_notes": notes,
    })


ROLES = ["FINANCIAL_APPROVER", "NONE", "SUPERVISOR_APPROVER"]  # rule 4': the request's approvals on file, or NONE
ROLES_ABROAD = [*ROLES, "VICE_CHANCELLOR_BUSINESS_FINANCE"]
LOW = ["AIR_BOOKING", "COMMERCIAL_AIR", "MOST_ECONOMICAL_RATES", "PRE_TRIP_APPROVAL"]
LOW_ABROAD = [*LOW, "INTERNATIONAL_TRAVEL"]
CABIN = ["AIR_BOOKING", "UPGRADES"]
TIMING = ["ARRIVAL_NEEDED_FOR_BUSINESS", "LOWEST_FARE"]
AGENCY = ["AIR_BOOKING", "APPENDIX_RECEIPTS"]
HOLD_REASONS = ["APPROVAL_REQUIRED", "PRE_TRIP_REQUEST_REQUIRED"]
SINGLE = "SINGLE_TRIP"

# ===== easy (5) =====

scenario(
    "birch-lantern", "easy", [],
    "I'm driving down to Denver and need a flight to Minneapolis on December 15th for the soil health workshop that "
    "starts the next morning. My pre-trip request is approved.",
    trip(traveller_name="Hannah Kessler", traveller_title="Extension Educator, Soil Health",
         destination="MSP", travel_date="2026-12-15", booking_date="2026-12-01",
         purpose="Upper Midwest soil health workshop in Minneapolis", purpose_kind="WORKSHOP",
         trip_request=request(SINGLE, "2026-11-12", "Workshop in Minneapolis, December 15-17; airfare, hotel and "
                              "registration on the center's extension funds"),
         sign_offs=approvals("Craig Whitmore", "Lori Baca", "2026-11-16")),
    search("DEN", "MSP", "2026-12-15", {
        "united": {"carrier": "UA", "depart": "07:10"},
        "delta": {"carrier": "DL", "depart": "09:45"},
        "southwest": {"carrier": "WN", "depart": "12:30"},
    }, [
        offer("united-economy", "united", "ECONOMY", 23800),
        offer("delta-economy", "delta", "ECONOMY", 21400),
        offer("southwest-economy", "southwest", "ECONOMY", 22600),
    ]),
    expected("BOOK", ["delta-economy"], ["ECONOMY"], ["LOWEST_FARE"], ROLES, LOW),
    [REQUEST, COACH_CAP],
    "The request is approved by the supervisor and financial approvers before booking (lines 143-145). The cheapest "
    "coach fare is the lowest listed price (lines 237-239): Delta at $214. No landing time matters (the workshop "
    "starts the next morning).")

scenario(
    "cobalt-meadow", "easy", [],
    "Denver to New York JFK on January 12th, please, for the grant review panel the next morning. Business class if "
    "the university allows it; if not, economy is fine. I have to be at the panel.",
    trip(traveller_name="Marcus Lindqvist", traveller_title="Professor of Economics, UNK",
         campus="University of Nebraska at Kearney (drives to Denver to fly)", destination="JFK",
         travel_date="2027-01-12", booking_date="2026-12-03", purpose="Federal grant review panel in New York",
         purpose_kind="MEETING", requested_cabin="BUSINESS",
         trip_request=request(SINGLE, "2026-11-18", "Grant review panel in New York, January 12-14"),
         sign_offs=approvals("Renee Dubois", "Arthur Coyle", "2026-11-20")),
    search("DEN", "JFK", "2027-01-12", {
        "jetblue": {"carrier": "B6", "depart": "07:00"},
        "delta": {"carrier": "DL", "depart": "08:15"},
        "american": {"carrier": "AA", "depart": "10:30"},
    }, [
        offer("jetblue-economy", "jetblue", "ECONOMY", 28900),
        offer("delta-economy", "delta", "ECONOMY", 31200),
        offer("delta-business", "delta", "BUSINESS", 114000),
        offer("american-economy", "american", "ECONOMY", 29800),
        offer("american-business", "american", "BUSINESS", 109000),
    ]),
    expected("BOOK", ["jetblue-economy"], ["ECONOMY"], ["TRAVELER_PAYS_UPGRADE", "UPGRADE_NOT_ELIGIBLE"], ROLES, CABIN),
    [COACH_CAP, REQUEST],
    "Lines 237-238: the ticket may not exceed the coach or main cabin price at purchase. Business fares ($1,090 and "
    "up) exceed every coach fare, so the traveller's fallback applies: the lowest coach fare, JetBlue at $289. The "
    "reason says why business is declined (UPGRADE_NOT_ELIGIBLE), not LOWEST_FARE.")

scenario(
    "dune-sparrow", "easy", [],
    "Please book me Denver to London Heathrow on January 18th for the pollinator research meeting at Rothamsted later "
    "that week. Economy is fine.",
    trip(traveller_name="Priya Raman", traveller_title="Assistant Professor of Entomology", destination="LHR",
         destination_needs_passport=True, travel_date="2027-01-18", booking_date="2026-12-01",
         purpose="Pollinator research meeting at Rothamsted Research, England", purpose_kind="RESEARCH",
         trip_request=request(SINGLE, "2026-11-09", "Research meeting in England, January 18-24; export control "
                              "review completed"),
         sign_offs=[*approvals("Craig Whitmore", "Lori Baca", "2026-11-12"), abroad("Dana Holloway", "2026-11-20")]),
    search("DEN", "LHR", "2027-01-18", {
        "united": {"carrier": "UA", "depart": "16:40"},
        "british": {"carrier": "BA", "depart": "19:05"},
    }, [
        offer("united-economy", "united", "ECONOMY", 78600),
        offer("united-business", "united", "BUSINESS", 412000),
        offer("british-economy", "british", "ECONOMY", 74200),
        offer("british-business", "british", "BUSINESS", 398000),
    ]),
    expected("BOOK", ["british-economy"], ["ECONOMY"], ["LOWEST_FARE"], ROLES_ABROAD, LOW_ABROAD),
    [REQUEST, INTL_VC, COACH_CAP],
    "England needs a passport and is outside the US: International Travel (lines 53-55). The request is approved by "
    "the supervisor and financial approvers, and the Vice Chancellor of Business and Finance approved the travel "
    "abroad (lines 151-153), all before booking. The lowest coach fare: British Airways at $742.")

scenario(
    "ember-thicket", "easy", [],
    "Denver to Seattle on January 26th for the western extension directors' meeting the next day, please. The cheapest "
    "seat that works.",
    trip(traveller_name="Tomas Avila", traveller_title="Associate Director, West Central Research, Extension and "
         "Education Center", campus="UNL West Central Research, Extension and Education Center, North Platte "
         "(drives to Denver to fly)", destination="SEA", travel_date="2027-01-26", booking_date="2026-12-08",
         purpose="Western region extension directors' meeting in Seattle", purpose_kind="MEETING",
         trip_request=request(SINGLE, "2026-11-30", "Regional meeting in Seattle, January 26-28"),
         sign_offs=approvals("Beth Sorensen", "Gary Imhoff", "2026-12-02")),
    search("DEN", "SEA", "2027-01-26", {
        "alaska": {"carrier": "AS", "depart": "07:00"},
        "united": {"carrier": "UA", "depart": "09:20"},
        "delta": {"carrier": "DL", "depart": "13:05"},
    }, [
        offer("alaska-economy", "alaska", "ECONOMY", 16800, seats=False),
        offer("united-economy", "united", "ECONOMY", 18400),
        offer("delta-economy", "delta", "ECONOMY", 19900),
    ]),
    expected("BOOK", ["united-economy"], ["ECONOMY"], ["LOWEST_FARE"], ROLES, LOW),
    [REQUEST, COACH_CAP],
    "The Alaska fare is sold out, so the lowest listed coach fare that can be bought is United at $184 (lines "
    "237-239). The request is approved (lines 143-145).")

scenario(
    "fern-gable", "easy", ["multi_leg"],
    "Book me Denver to Atlanta on February 2nd; the conference starts the morning of the 3rd. I don't mind a "
    "connection if it's the cheapest.",
    trip(traveller_name="Owen Fairbanks", traveller_title="Research Technologist, Agronomy", destination="ATL",
         travel_date="2027-02-02", booking_date="2026-12-04", purpose="Southern weed science conference in Atlanta",
         trip_request=request(SINGLE, "2026-11-23", "Conference in Atlanta, February 2-5"),
         sign_offs=approvals("Craig Whitmore", "Lori Baca", "2026-11-25")),
    search("DEN", "ATL", "2027-02-02", {
        "chicago": {"carrier": "UA", "via": ["ORD"], "depart": "07:30", "layovers": [75]},
        "delta": {"carrier": "DL", "depart": "08:00"},
        "southwest": {"carrier": "WN", "depart": "11:00"},
    }, [
        offer("chicago-economy", "chicago", "ECONOMY", 21900),
        offer("delta-economy", "delta", "ECONOMY", 27600),
        offer("southwest-economy", "southwest", "ECONOMY", 24800),
    ]),
    expected("BOOK", ["chicago-economy"], ["ECONOMY"], ["LOWEST_FARE"], ROLES, LOW),
    [REQUEST, COACH_CAP, ECONOMICAL],
    "The lowest listed coach fare is United via Chicago at $219 (lines 237-239); the traveller welcomes a connection "
    "and the conference starts the next morning, so it meets the trip's goals (lines 160-162).")

# ===== boundary twins (6) =====

PREMIUM_REQUEST = ("Denver to Washington Dulles on January 20th for the USDA program meeting the next morning. I'd "
                   "like premium economy if the university will pay for it; otherwise economy is fine.")


def dulles(premium_cents):
    return search("DEN", "IAD", "2027-01-20", {
        "morning": {"carrier": "UA", "depart": "08:05"},
        "southwest": {"carrier": "WN", "depart": "10:15"},
        "afternoon": {"carrier": "UA", "depart": "13:40"},
    }, [
        offer("morning-economy", "morning", "ECONOMY", 26400),
        offer("morning-premium", "morning", "PREMIUM_ECONOMY", premium_cents),
        offer("southwest-economy", "southwest", "ECONOMY", 27900),
        offer("afternoon-economy", "afternoon", "ECONOMY", 30100),
        offer("afternoon-premium", "afternoon", "PREMIUM_ECONOMY", 38900),
    ], background=0)


def dulles_trip():
    return trip(traveller_name="Grace Okafor", traveller_title="Extension Specialist, Farm Programs",
                destination="IAD", travel_date="2027-01-20", booking_date="2026-12-02",
                purpose="USDA extension program meeting in Washington", purpose_kind="MEETING",
                requested_cabin="PREMIUM_ECONOMY",
                trip_request=request(SINGLE, "2026-11-17", "Program meeting in Washington, January 20-22"),
                sign_offs=approvals("Craig Whitmore", "Lori Baca", "2026-11-19"))


scenario(
    "garnet-reed", "boundary_twin", [], PREMIUM_REQUEST, dulles_trip(), dulles(26400),
    expected("BOOK", ["morning-premium"], ["PREMIUM_ECONOMY"], ["LOWEST_FARE", "PREMIUM_ECONOMY_ALLOWED",
                                                                "UPGRADE_WITHIN_FARE_MARGIN"], ROLES,
             [*CABIN, "MOST_ECONOMICAL_RATES"]),
    [COACH_CAP, REQUEST],
    "Lines 237-238 cap the ticket at the coach or main cabin price at purchase ('not to exceed': inclusive). The 08:05 "
    "premium economy fare is $264, the same as the coach fare on that flight, which is also the lowest listed price; "
    "it does not exceed the coach rate, so the cabin the traveller asks for is allowed.",
    twin_of="heron-slate", twin_fact="08:05 premium economy fare 26400 or 26500 cents (coach on that flight 26400)")

scenario(
    "heron-slate", "boundary_twin", [], PREMIUM_REQUEST, dulles_trip(), dulles(26500),
    expected("BOOK", ["morning-economy"], ["ECONOMY"], ["TRAVELER_PAYS_UPGRADE", "UPGRADE_NOT_ELIGIBLE"], ROLES, CABIN),
    [COACH_CAP, REQUEST],
    "The 08:05 premium economy fare is $265, one dollar above the $264 coach fare, which is also the lowest listed "
    "price: it exceeds the coach rate (lines 237-238), so the fallback applies: the lowest coach fare. The reason says "
    "why premium economy is declined.",
    twin_of="garnet-reed", twin_fact="08:05 premium economy fare 26500 or 26400 cents (coach on that flight 26400)")

BOSTON_REQUEST = ("I need to get from Denver to Boston on January 27th for the extension conference's evening poster "
                  "session. I have to land by 5 pm to set up my poster. Book what the policy allows.")


def boston(depart):
    return search("DEN", "BOS", "2027-01-27", {
        "minneapolis": {"carrier": "DL", "via": ["MSP"], "depart": depart, "minutes": [125, 165], "layovers": [70]},
        "united": {"carrier": "UA", "depart": "07:30", "minutes": [240]},
        "jetblue": {"carrier": "B6", "depart": "10:40", "minutes": [235]},
    }, [
        offer("minneapolis-economy", "minneapolis", "ECONOMY", 25400),
        offer("united-economy", "united", "ECONOMY", 38900),
        offer("jetblue-economy", "jetblue", "ECONOMY", 34200),
    ], background=0)


def boston_trip():
    return trip(traveller_name="Lucy Hartmann", traveller_title="Extension Educator, Water Quality",
                destination="BOS", travel_date="2027-01-27", booking_date="2026-12-03",
                purpose="Poster at the evening session of the national extension conference in Boston",
                must_arrive_by="2027-01-27 17:00",
                trip_request=request(SINGLE, "2026-11-19", "Conference in Boston, January 27-29"),
                sign_offs=approvals("Craig Whitmore", "Lori Baca", "2026-11-23"))


scenario(
    "iris-copper", "boundary_twin", ["multi_leg"], BOSTON_REQUEST, boston_trip(), boston("08:35"),
    expected("BOOK", ["minneapolis-economy"], ["ECONOMY"], ["LOWEST_FARE"], ROLES, LOW),
    [COACH_CAP, ECONOMICAL, REQUEST],
    "The cheapest coach fare, Delta via Minneapolis at $254, leaves 08:35 and lands in Boston at 16:35, before the 17:00 "
    "the traveller must land by. It is the lowest listed price and meets the trip's goals (lines 160-162, 237-239).",
    twin_of="juniper-wold", twin_fact="the Delta connection leaves 08:35 or 09:25 (lands 16:35 or 17:25)")

scenario(
    "juniper-wold", "boundary_twin", ["multi_leg", "dearer_option"], BOSTON_REQUEST, boston_trip(), boston("09:25"),
    expected("BOOK", ["jetblue-economy"], ["ECONOMY"], TIMING, ROLES, [*LOW]),
    [COACH_CAP, ECONOMICAL, REQUEST],
    "The cheapest coach fare (Delta via Minneapolis, $254) now leaves 09:25 and lands at 17:25, after the 17:00 the "
    "traveller must land by, so it does not meet the trip's goals (lines 160-162). The most economical flight that "
    "does is JetBlue at $342, landing 16:35; it is not the lowest listed price, and the deadline is the brief "
    "explanation lines 238-239 ask for.",
    twin_of="iris-copper", twin_fact="the Delta connection leaves 09:25 or 08:35 (lands 17:25 or 16:35)")

FRANKFURT_REQUEST = ("Denver to Frankfurt on February 8th, please. Our project kickoff at the Frankfurt institute is at "
                     "noon on the 9th and I need to land by 10 am. Book what the policy allows.")


def frankfurt(depart):
    return search("DEN", "FRA", "2027-02-08", {
        "dulles": {"carrier": "UA", "via": ["IAD"], "depart": depart, "minutes": [235, 500], "layovers": [90]},
        "lufthansa": {"carrier": "LH", "depart": "14:50", "minutes": [600]},
    }, [
        offer("dulles-economy", "dulles", "ECONOMY", 81200),
        offer("lufthansa-economy", "lufthansa", "ECONOMY", 104600),
        offer("lufthansa-business", "lufthansa", "BUSINESS", 462000),
    ], background=0)


def frankfurt_trip():
    return trip(traveller_name="Daniel Brecht", traveller_title="Research Associate Professor, Biological Systems "
                "Engineering", destination="FRA", destination_needs_passport=True, travel_date="2027-02-08",
                booking_date="2026-12-07", purpose="Kickoff of a joint irrigation sensing project in Frankfurt",
                purpose_kind="RESEARCH", must_arrive_by="2027-02-09 10:00",
                trip_request=request(SINGLE, "2026-11-10", "Project kickoff in Germany, February 8-13; export "
                                     "control review completed"),
                sign_offs=[*approvals("Craig Whitmore", "Lori Baca", "2026-11-13"),
                           abroad("Dana Holloway", "2026-11-24")])


scenario(
    "kestrel-moor", "boundary_twin", ["multi_leg", "date_arithmetic"], FRANKFURT_REQUEST, frankfurt_trip(),
    frankfurt("11:00"),
    expected("BOOK", ["dulles-economy"], ["ECONOMY"], ["LOWEST_FARE"], ROLES_ABROAD, LOW_ABROAD),
    [COACH_CAP, ECONOMICAL, REQUEST, INTL_VC],
    "International Travel with every approval on file (lines 143-145, 151-153). The cheapest coach fare, United via "
    "Dulles at $812, leaves 11:00 on February 8th and lands 08:45 local on the 9th, before 10:00: it is the lowest "
    "listed price and meets the trip's goals.",
    twin_of="linden-shoal", twin_fact="the United connection leaves 11:00 or 13:30 (lands 08:45 or 11:15 the next day)")

scenario(
    "linden-shoal", "boundary_twin", ["multi_leg", "date_arithmetic", "dearer_option"], FRANKFURT_REQUEST,
    frankfurt_trip(), frankfurt("13:30"),
    expected("BOOK", ["lufthansa-economy"], ["ECONOMY"], TIMING, ROLES_ABROAD, LOW_ABROAD),
    [COACH_CAP, ECONOMICAL, REQUEST, INTL_VC],
    "The cheapest coach fare (United via Dulles, $812) now leaves 13:30 and lands 11:15 local on the 9th, after the "
    "10:00 the traveller must land by (lines 160-162). The Lufthansa nonstop at $1,046 lands 08:50: the most economical "
    "flight that meets the trip's goals, with the deadline as the explanation lines 238-239 ask for.",
    twin_of="kestrel-moor", twin_fact="the United connection leaves 13:30 or 11:00 (lands 11:15 or 08:45 the next day)")

# ===== multi-rule (4) =====

PARIS = search("DEN", "CDG", "2027-01-11", {
    "airfrance": {"carrier": "AF", "depart": "17:10"},
    "dulles": {"carrier": "UA", "via": ["IAD"], "depart": "12:00", "layovers": [85]},
}, [
    offer("airfrance-economy", "airfrance", "ECONOMY", 73400),
    offer("airfrance-business", "airfrance", "BUSINESS", 389000),
    offer("dulles-economy", "dulles", "ECONOMY", 78100),
], background=0)

scenario(
    "maple-cinder", "multi_rule", ["outside_air_section"],
    "I'm flying Denver to Paris on January 11th for the soil carbon workshop at INRAE, which starts on the 13th. Air "
    "France's own website has my "
    "flight for $689, less than the agency's price, so I'd like to buy it there myself and claim it back. If that "
    "isn't allowed, book it through the agency; I have to be at the workshop.",
    trip(traveller_name="Elise Marchetti", traveller_title="Associate Professor of Soil Science",
         destination="CDG", destination_needs_passport=True, travel_date="2027-01-11", booking_date="2026-12-07",
         purpose="Soil carbon workshop at INRAE near Paris", purpose_kind="WORKSHOP", wants_to_book_outside=True,
         outside_fares=[{"source": "Air France website", "flight_number": first_flight("maple-cinder", PARIS,
                                                                                       "airfrance-economy"),
                         "fare_cents": 68900, "found_on": "2026-12-07"}],
         trip_request=request(SINGLE, "2026-11-05", "Workshop in France, January 13-16, flying out January 11; "
                              "export control review completed"),
         sign_offs=[*approvals("Craig Whitmore", "Lori Baca", "2026-11-09"), abroad("Dana Holloway", "2026-11-18")]),
    PARIS,
    expected("BOOK", ["airfrance-economy"], ["ECONOMY"], ["TRAVEL_AGENCY_REQUIRED"], ROLES_ABROAD,
             [*AGENCY, "INTERNATIONAL_TRAVEL"]),
    [INTL_AGENCY, APPENDIX_AIR, INTL_VC, REQUEST, COACH_CAP],
    "Lines 222-225: international flights are booked through the contracted agency, and outside it only when the "
    "required flights are not available there. The agency lists the same Air France flight, so the same-day cheaper "
    "comparison (written for domestic air, lines 228-234) does not open the outside purchase; the fallback is the "
    "agency's lowest coach fare, Air France at $734. All approvals, the Vice Chancellor's included, are on file.",
    distractors=[CANCEL])

scenario(
    "nutmeg-ridge", "multi_rule", ["upgrade_not_taken"],
    "Denver to Tokyo Narita on February 15th for the rice genomics symposium, which opens on the 18th. I'd like "
    "business class, and I'll pay the "
    "difference myself. If the university can't book that, book what's allowed; I have to be at the symposium.",
    trip(traveller_name="Kenji Morimoto", traveller_title="Professor of Plant Pathology", destination="NRT",
         destination_needs_passport=True, travel_date="2027-02-15", booking_date="2026-12-09",
         purpose="Rice genomics symposium in Tokyo", purpose_kind="CONFERENCE", requested_cabin="BUSINESS",
         traveller_pays_upgrade=True,
         trip_request=request(SINGLE, "2026-11-06", "Symposium in Japan, February 18-21, flying out February 15; "
                              "export control review completed"),
         sign_offs=[*approvals("Craig Whitmore", "Lori Baca", "2026-11-10"), abroad("Dana Holloway", "2026-11-19")]),
    search("DEN", "NRT", "2027-02-15", {
        "united": {"carrier": "UA", "depart": "11:20"},
        "ana": {"carrier": "NH", "depart": "12:35"},
    }, [
        offer("united-economy", "united", "ECONOMY", 118000),
        offer("united-business", "united", "BUSINESS", 520000),
        offer("ana-economy", "ana", "ECONOMY", 109500),
        offer("ana-business", "ana", "BUSINESS", 498000),
    ], background=0),
    expected("BOOK", ["ana-economy"], ["ECONOMY"], ["TRAVELER_PAYS_UPGRADE", "UPGRADE_NOT_ELIGIBLE"], ROLES_ABROAD,
             [*CABIN, "INTERNATIONAL_TRAVEL"]),
    [COACH_CAP, UPGRADES, INTL_VC, REQUEST],
    "Lines 237-238: the ticket the University buys may not exceed the coach price. Lines 241-244: an upgrade is the "
    "traveller's own, arranged afterwards as a ticket exchange with the agency and paid by them. So the University "
    "books the lowest coach fare, ANA at $1,095, and the traveller may upgrade it at their own cost. The Vice "
    "Chancellor's approval of the travel abroad is on file.")

SALT_LAKE = search("DEN", "SLC", "2027-01-14", {
    "delta": {"carrier": "DL", "depart": "07:00"},
    "united": {"carrier": "UA", "depart": "09:30"},
    "southwest": {"carrier": "WN", "depart": "11:45"},
}, [
    offer("delta-economy", "delta", "ECONOMY", 19800),
    offer("united-economy", "united", "ECONOMY", 17600),
    offer("southwest-economy", "southwest", "ECONOMY", 18900),
])

scenario(
    "opal-fjord", "multi_rule", ["outside_air_section"],
    "I'd still rather our team chartered a small plane to Salt Lake City on January 14th for the water rights hearing "
    "the next morning. If a charter isn't possible, put me on a regular airline flight; I have to be at the hearing.",
    trip(traveller_name="Ruth Delgado", traveller_title="Water Resources Engineer, Panhandle center",
         destination="SLC", travel_date="2027-01-14", booking_date="2026-12-02",
         purpose="Water rights hearing in Salt Lake City", purpose_kind="HEARING", requested_mode="CHARTERED_PLANE",
         trip_request=request(SINGLE, "2026-11-20", "Hearing in Salt Lake City, January 14-15; the team's wish "
                              "to charter a plane is noted, with no approval for it"),
         sign_offs=approvals("Craig Whitmore", "Lori Baca", "2026-11-24")),
    SALT_LAKE,
    expected("BOOK", ["united-economy"], ["ECONOMY"], ["LOWEST_FARE", "PRIVATE_AIRCRAFT_NOT_APPROVED"], ROLES,
             ["COMMERCIAL_AIR", "MOST_ECONOMICAL_RATES", "OTHER_FORMS_OF_TRAVEL", "PRE_TRIP_APPROVAL"]),
    [PLANES, OTHER_FORMS, COMMERCIAL, REQUEST, COACH_CAP],
    "Lines 156-158: chartered planes need additional approval from the Vice Chancellor of Business and Finance, and "
    "lines 316-321 need a request affirming no more economical means; none is on file. Lines 208-211 expect "
    "commercial airlines, and the traveller's fallback is a regular flight: the lowest coach fare, United at $176. "
    "The reason says why the charter is declined.")

PHOENIX = search("DEN", "PHX", "2027-01-07", {
    "southwest": {"carrier": "WN", "depart": "08:10"},
    "american": {"carrier": "AA", "depart": "10:20"},
    "united": {"carrier": "UA", "depart": "14:00"},
}, [
    offer("southwest-economy", "southwest", "ECONOMY", 18600),
    offer("american-economy", "american", "ECONOMY", 20300),
    offer("united-economy", "united", "ECONOMY", 21900),
], background=0)

scenario(
    "pewter-glen", "multi_rule", ["date_arithmetic", "month_end"],
    "Denver to Phoenix on January 7th for the desert agriculture meeting the next morning. On November 28th I found my "
    "Southwest flight on Expedia for $171, everything included, less than the agency is charging today, so I'd "
    "like to buy it myself. If I can't, book it through the agency.",
    trip(traveller_name="Neil Ashworth", traveller_title="Extension Educator, Cropping Systems", destination="PHX",
         travel_date="2027-01-07", booking_date="2026-12-01", purpose="Desert agriculture research meeting in Phoenix",
         purpose_kind="MEETING", wants_to_book_outside=True,
         outside_fares=[{"source": "Expedia", "flight_number": first_flight("pewter-glen", PHOENIX, "southwest-economy"),
                         "fare_cents": 17100, "found_on": "2026-11-28"}],
         trip_request=request(SINGLE, "2026-11-16", "Meeting in Phoenix, January 7-9"),
         sign_offs=approvals("Craig Whitmore", "Lori Baca", "2026-11-18")),
    PHOENIX,
    expected("BOOK", ["southwest-economy"], ["ECONOMY"], ["OUTSIDE_FARE_COMPARISON_NOT_MET", "TRAVEL_AGENCY_REQUIRED"],
             ROLES, AGENCY),
    [OUTSIDE_DOMESTIC, APPENDIX_AIR, REQUEST, COACH_CAP],
    "Lines 228-234: buying domestic air outside the agency needs proof of a comparable, less expensive fare, all fees "
    "included, and 'These comparisons must be completed on the same day'. The traveller's fare is from November 28th; "
    "today is December 1st, three days later, so the comparison does not qualify. The fallback: the agency's lowest "
    "coach fare, the same Southwest flight at $186.",
    distractors=[CANCEL])

# ===== hidden clause (2) =====

scenario(
    "quartz-bramble", "hidden_clause", ["outside_air_section"],
    "I'm the keynote speaker at your irrigation workshop; my talk is on the 4th. Please book me Seattle to Denver on "
    "February 3rd, business class as I always fly; if the university can't, economy is fine. I have to be there.",
    trip(traveller_name="Dr. Lena Ortiz", traveller_title="Keynote speaker under contract for the workshop",
         passenger="CONTRACTED_SPEAKER", campus="Hosted by the UNL Panhandle Research, Extension and Education "
         "Center, Scottsbluff", origin="SEA", destination="DEN", travel_date="2027-02-03", booking_date="2026-12-08",
         purpose="Keynote at the Panhandle irrigation workshop (driven from Denver to Scottsbluff)",
         purpose_kind="WORKSHOP", requested_cabin="BUSINESS",
         trip_request=request(SINGLE, "2026-11-30", "The center's request for its contracted keynote speaker's "
                              "travel, February 3-5"),
         sign_offs=approvals("Craig Whitmore", "Lori Baca", "2026-12-02")),
    search("SEA", "DEN", "2027-02-03", {
        "alaska": {"carrier": "AS", "depart": "07:30"},
        "united": {"carrier": "UA", "depart": "09:10"},
        "delta": {"carrier": "DL", "depart": "12:40"},
    }, [
        offer("alaska-economy", "alaska", "ECONOMY", 17200),
        offer("united-economy", "united", "ECONOMY", 19400),
        offer("united-business", "united", "BUSINESS", 61800),
        offer("delta-economy", "delta", "ECONOMY", 18600),
        offer("delta-business", "delta", "BUSINESS", 58500),
    ]),
    expected("BOOK", ["alaska-economy"], ["ECONOMY"], ["TRAVELER_PAYS_UPGRADE", "UPGRADE_NOT_ELIGIBLE"], ROLES,
             [*CABIN, "NON_UNIVERSITY_PERSONNEL"]),
    [NON_UNIVERSITY, COACH_CAP, REQUEST],
    "Lines 103-106: speakers who have contracted with the University for an event are expected to comply with the "
    "policy. So the coach cap of lines 237-238 applies: business fares exceed the coach price, and the speaker's "
    "fallback gives the lowest coach fare, Alaska at $172.")

scenario(
    "russet-dell", "hidden_clause", ["outside_air_section", "dearer_option"],
    "Denver to Houston on January 21st for the rural health meeting the next morning. Under my accommodation plan I "
    "fly in the business cabin; please book that.",
    trip(traveller_name="Sandra Whitfield", traveller_title="Research Associate Professor, Rural Health, UNK",
         campus="University of Nebraska at Kearney (drives to Denver to fly)", destination="IAH",
         travel_date="2027-01-21", booking_date="2026-12-03", purpose="Rural health research meeting in Houston",
         purpose_kind="MEETING", requested_cabin="BUSINESS",
         trip_request=request(SINGLE, "2026-11-19", "Meeting in Houston, January 21-23; includes the business-cabin "
                              "seat set out in the traveller's accommodation plan"),
         sign_offs=[*approvals("Renee Dubois", "Arthur Coyle", "2026-11-23"),
                    sign("ADA_COORDINATOR", "Paul Iverson", "ACCOMMODATION", "ADA accommodation plan on file: a "
                         "business-cabin seat on University flights; its written description was sent to the "
                         "University Travel Office", "2026-10-05")]),
    search("DEN", "IAH", "2027-01-21", {
        "morning": {"carrier": "UA", "depart": "07:15"},
        "southwest": {"carrier": "WN", "depart": "09:50"},
        "midday": {"carrier": "UA", "depart": "12:40"},
    }, [
        offer("morning-economy", "morning", "ECONOMY", 22100),
        offer("morning-business", "morning", "BUSINESS", 61200),
        offer("southwest-economy", "southwest", "ECONOMY", 20500),
        offer("midday-economy", "midday", "ECONOMY", 24800),
        offer("midday-business", "midday", "BUSINESS", 57500),
    ]),
    expected("BOOK", ["midday-business"], ["BUSINESS"], ["MEDICAL_NEED", "POLICY_EXEMPTION_DOCUMENTED"],
             [*ROLES, "ADA_COORDINATOR", "UNIVERSITY_TRAVEL_OFFICE"],
             ["COMPLIANCE_AND_EXEMPTIONS", "MOST_ECONOMICAL_RATES", "PRE_TRIP_APPROVAL"]),
    [EXEMPTION, REQUEST],
    "Lines 118-123: exemptions are authorized with documentation such as an ADA accommodation plan on file with the "
    "campus ADA/504 coordinator, who gives the University Travel Office a written description, and the request is "
    "approved incorporating it. All of that is on file, so the coach cap gives way: the cheapest business fare, "
    "United 12:40 at $575.")

# ===== distractor (2) =====

scenario(
    "sorrel-pike", "distractor", ["date_arithmetic", "month_end"],
    "The partner university in Wageningen moved our meeting up, so I only filed my pre-trip request this week; "
    "everything is approved now. Please book Denver to Amsterdam on December 14th. The meeting is on the 16th.",
    trip(traveller_name="Joanna Pierce", traveller_title="Assistant Professor of Animal Science", destination="AMS",
         destination_needs_passport=True, travel_date="2026-12-14", booking_date="2026-11-27",
         purpose="Research partnership meeting at Wageningen University, Netherlands", purpose_kind="RESEARCH",
         trip_request=request(SINGLE, "2026-11-25", "Partnership meeting in the Netherlands, December 14-18; "
                              "export control review completed"),
         sign_offs=[*approvals("Craig Whitmore", "Lori Baca", "2026-11-25"), abroad("Dana Holloway", "2026-11-26")]),
    search("DEN", "AMS", "2026-12-14", {
        "klm": {"carrier": "KL", "depart": "15:20"},
        "dulles": {"carrier": "UA", "via": ["IAD"], "depart": "11:10", "layovers": [95]},
    }, [
        offer("klm-economy", "klm", "ECONOMY", 86400),
        offer("dulles-economy", "dulles", "ECONOMY", 91800),
    ]),
    expected("BOOK", ["klm-economy"], ["ECONOMY"], ["LOWEST_FARE"], ROLES_ABROAD, LOW_ABROAD),
    [REQUEST, INTL_VC, COACH_CAP],
    "The request was filed November 25th for a December 14th departure: 19 days ahead, under the 30 days lines "
    "148-151 and 450-452 advise ('well-advised', 'should'). That advice protects the approvals, and every approval, the "
    "Vice Chancellor's included, is already on file, so the late filing changes nothing: the lowest coach fare, KLM "
    "at $864.",
    distractors=[THIRTY_DAYS, THIRTY_AGAIN, INSURANCE])

scenario(
    "tansy-bluff", "distractor", ["upgrade_not_taken"],
    "Denver to Dallas on January 19th for the beef cattle workshop the next day. It's a short flight, so regular "
    "economy is fine this time, even though my accommodation plan covers the business cabin.",
    trip(traveller_name="Wade Lindgren", traveller_title="Extension Educator, Beef Systems", destination="DFW",
         travel_date="2027-01-19", booking_date="2026-12-04", purpose="Beef cattle production workshop in Dallas",
         purpose_kind="WORKSHOP",
         trip_request=request(SINGLE, "2026-11-20", "Workshop in Dallas, January 19-21"),
         sign_offs=[*approvals("Craig Whitmore", "Lori Baca", "2026-11-24"),
                    sign("ADA_COORDINATOR", "Paul Iverson", "ACCOMMODATION", "ADA accommodation plan on file: a "
                         "business-cabin seat on University flights when the traveller wants it; its written "
                         "description was sent to the University Travel Office", "2026-09-14")]),
    search("DEN", "DFW", "2027-01-19", {
        "american": {"carrier": "AA", "depart": "06:15"},
        "united": {"carrier": "UA", "depart": "08:40"},
        "southwest": {"carrier": "WN", "depart": "10:05"},
    }, [
        offer("american-economy", "american", "ECONOMY", 16900),
        offer("american-business", "american", "BUSINESS", 48000),
        offer("united-economy", "united", "ECONOMY", 18200),
        offer("united-business", "united", "BUSINESS", 51000),
        offer("southwest-economy", "southwest", "ECONOMY", 17500),
    ]),
    expected("BOOK", ["american-economy"], ["ECONOMY"], ["LOWEST_FARE"], [*ROLES, "ADA_COORDINATOR"], LOW),
    [REQUEST, COACH_CAP],
    "The traveller asks for economy. The accommodation (lines 118-123) would allow the business cabin, but it is not "
    "asked for, so it does not change the answer: the lowest coach fare, American 06:15 at $169 (lines 237-239). The "
    "06:15 departure's breakfast allowance (line 372) is a meal rule, not a fare rule. The coordinator's sign-off is "
    "on file but unused, so ADA_COORDINATOR is accepted beside NONE (rule 4(b)).",
    distractors=[aside(118, 120, "Exemptions to this Travel Policy will only be authorized with proper "
                                     "documentation, such as an ADA accommodation plan", "permits more; not asked for"),
                 MEALS, DEADLINE])

# ===== refusal (2) =====

scenario(
    "umber-loch", "refusal", ["personal_travel", "outside_air_section"],
    "I'm going with my husband, Professor Daniel Reyes, to his conference in San Diego. Could you book me Denver to "
    "San Diego on February 10th?",
    trip(traveller_name="Maria Reyes", traveller_title="Spouse of Professor Daniel Reyes", passenger="COMPANION",
         accompanies="Daniel Reyes, Professor of Agricultural Economics", destination="SAN", travel_date="2027-02-10",
         booking_date="2026-12-07", purpose="Going along with her husband to his conference in San Diego",
         purpose_kind="PERSONAL",
         trip_request=request(SINGLE, "2026-11-24", "Professor Reyes's conference in San Diego, February 10-13"),
         sign_offs=approvals("Craig Whitmore", "Lori Baca", "2026-11-26")),
    search("DEN", "SAN", "2027-02-10", {
        "united": {"carrier": "UA", "depart": "08:25"},
        "southwest": {"carrier": "WN", "depart": "11:10"},
    }, [
        offer("united-economy", "united", "ECONOMY", 19700),
        offer("southwest-economy", "southwest", "ECONOMY", 17900),
    ]),
    expected("REFUSE", [], ["NONE"], ["COMPANION_NOT_COVERED", "OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED"],
             ROLES, ["APPENDIX_RECEIPTS", "DEFINITIONS", "PERSONAL_TRAVEL", "POLICY_STATEMENT", "SCOPE"]),
    [POLICY_STATEMENT, PERSONAL, SPOUSE_ROW],
    "Lines 26-28: the University pays for travel incurred in the performance of University business; lines 164-170 pay "
    "only the business portion; the appendix lists spouse/companion expenses as not reimbursable (lines 762-764). The "
    "spouse's flight is no University business: buy nothing. The professor's approvals are on file but unused (rule "
    "4(b): NONE or those roles).",
    distractors=[LODGING_COMPANION])

scenario(
    "vetch-hollow", "refusal", ["personal_travel", "outside_air_section"],
    "I'm in Chicago for the two-week program at the agricultural research center. On the free weekend I want to fly to "
    "Seattle on Saturday, February 13th, to see my sister, and come back Sunday. Could you book Chicago to Seattle for "
    "Saturday?",
    trip(traveller_name="Caleb Norquist", traveller_title="Research Technician, Plant Breeding", origin="ORD",
         destination="SEA", travel_date="2027-02-13", booking_date="2026-12-09",
         purpose="Visiting his sister in Seattle over the free weekend of a two-week program in Chicago",
         purpose_kind="PERSONAL",
         trip_request=request(SINGLE, "2026-11-30", "Two-week training program in Chicago, February 8-19; a "
                              "personal weekend trip is disclosed and its costs left out"),
         sign_offs=approvals("Craig Whitmore", "Lori Baca", "2026-12-02")),
    search("ORD", "SEA", "2027-02-13", {
        "united": {"carrier": "UA", "depart": "08:00"},
        "alaska": {"carrier": "AS", "depart": "10:35"},
    }, [
        offer("united-economy", "united", "ECONOMY", 21300),
        offer("alaska-economy", "alaska", "ECONOMY", 19600),
    ]),
    expected("REFUSE", [], ["NONE"], ["OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED"], ROLES,
             ["DEFINITIONS", "PERSONAL_TRAVEL", "POLICY_STATEMENT", "SCOPE"]),
    [PERSONAL, POLICY_STATEMENT],
    "Lines 164-170: personal travel while in Travel Status is disclosed in the request, but only University "
    "business-related expenses are paid. The Seattle weekend is wholly personal: buy nothing. The program's approvals "
    "are on file but unused (rule 4(b)).",
    distractors=[DIRECT_PAY])

# ===== flag (3) =====

scenario(
    "willow-crag", "flag", ["approval_required", "outside_air_section"],
    "Denver to Toronto on February 15th for the plant pathology conference, which opens the next morning. My "
    "supervisor and financial approver have "
    "both approved my pre-trip request, so please go ahead and book it.",
    trip(traveller_name="Natalie Brooks", traveller_title="Assistant Professor of Plant Pathology", destination="YYZ",
         destination_needs_passport=True, travel_date="2027-02-15", booking_date="2026-12-02",
         purpose="Plant pathology conference in Toronto", purpose_kind="CONFERENCE",
         trip_request=request(SINGLE, "2026-11-16", "Conference in Toronto, Canada, February 15-18; export control "
                              "review completed"),
         sign_offs=approvals("Craig Whitmore", "Lori Baca", "2026-11-19")),
    search("DEN", "YYZ", "2027-02-15", {
        "aircanada": {"carrier": "AC", "depart": "08:10"},
        "united": {"carrier": "UA", "depart": "11:25"},
    }, [
        offer("aircanada-economy", "aircanada", "ECONOMY", 31800),
        offer("united-economy", "united", "ECONOMY", 34500),
    ], background=0),
    expected("FLAG_FOR_APPROVAL", ["aircanada-economy"], ["ECONOMY"], HOLD_REASONS,
             ["VICE_CHANCELLOR_BUSINESS_FINANCE"], ["DEFINITIONS", "INTERNATIONAL_TRAVEL", "PRE_TRIP_APPROVAL"]),
    [INTL_DEFINED, INTL_VC, REQUEST],
    "Canada is outside the United States and needs a passport: International Travel (lines 53-55), which 'will "
    "require additional approval from the Traveler's respective Vice Chancellor of Business and Finance or their "
    "designee(s)' (lines 151-153). Only the supervisor and financial approver have signed, and the request must be "
    "approved before any booking (lines 143-145). Hold the lowest coach fare, Air Canada at $318, for the Vice "
    "Chancellor. Approval required, not 'no compliant offer'.",
    flag_twins=["dune-sparrow", "birch-lantern"],
    ambiguity="none: the Vice Chancellor's approval of International Travel is required and missing; the text is clear")

scenario(
    "yarrow-flint", "flag", ["approval_required", "outside_air_section"],
    "My blanket travel authorization is approved for the year, so please book me Denver to Austin on January 25th for "
    "the regional extension conference, which opens the next morning.",
    trip(traveller_name="Doug Hensley", traveller_title="Extension Educator, Youth Programs",
         campus="Nebraska Extension, Kearney office (drives to Denver to fly)", destination="AUS",
         travel_date="2027-01-25", booking_date="2026-12-03",
         purpose="Southern region extension conference in Austin", purpose_kind="EXTENSION_PROGRAM",
         trip_request=request("BLANKET", "2026-07-01", "Extension program visits to county offices across Nebraska "
                              "for the fiscal year July 2026 to June 2027"),
         sign_offs=approvals("Beth Sorensen", "Gary Imhoff", "2026-07-02",
                             covers="The blanket authorization for the fiscal year, approved")),
    search("DEN", "AUS", "2027-01-25", {
        "southwest": {"carrier": "WN", "depart": "08:20"},
        "dallas": {"carrier": "AA", "via": ["DFW"], "depart": "07:05", "layovers": [65]},
        "united": {"carrier": "UA", "depart": "11:00"},
    }, [
        offer("southwest-economy", "southwest", "ECONOMY", 15900),
        offer("dallas-economy", "dallas", "ECONOMY", 17400),
        offer("united-economy", "united", "ECONOMY", 18700),
    ], background=0),
    expected("FLAG_FOR_APPROVAL", ["southwest-economy"], ["ECONOMY"], HOLD_REASONS,
             ["FINANCIAL_APPROVER", "SUPERVISOR_APPROVER"], ["BLANKET_AUTHORIZATION", "PRE_TRIP_APPROVAL"]),
    [BLANKET, EACH_TRIP, REQUEST],
    "Lines 177-181: a Blanket Travel Authorization covers travel within city limits, a 100-mile radius of the campus "
    "and/or State limits; 'Travel not meeting this criteria must be requested through the standard, individual trip "
    "process'. A flight from Denver to Austin is out of state, so it needs its own request approved by the supervisor "
    "and financial approvers before any booking (lines 136-137, 143-145). Hold the lowest coach fare, Southwest at "
    "$159, for those approvals.",
    flag_twins=["birch-lantern", "ember-thicket"],
    ambiguity="none: an individual request's approvals are required and missing; the text is clear")

scenario(
    "zinnia-marsh", "flag", ["unclear_phrase"],
    "Denver to Honolulu on February 22nd for the tropical plant disease symposium, which opens the next morning. "
    "My supervisor and financial "
    "approver approved the pre-trip request. Please book it.",
    trip(traveller_name="Iris Kahananui", traveller_title="Research Assistant Professor, Plant Pathology",
         destination="HNL", travel_date="2027-02-22", booking_date="2026-12-04",
         purpose="Tropical plant disease symposium in Honolulu", purpose_kind="CONFERENCE",
         trip_request=request(SINGLE, "2026-11-02", "Symposium in Honolulu, Hawaii, February 22-26"),
         sign_offs=approvals("Craig Whitmore", "Lori Baca", "2026-11-05")),
    search("DEN", "HNL", "2027-02-22", {
        "united": {"carrier": "UA", "depart": "09:15"},
        "alaska": {"carrier": "AS", "depart": "11:40"},
    }, [
        offer("united-economy", "united", "ECONOMY", 41800),
        offer("alaska-economy", "alaska", "ECONOMY", 39600),
    ], background=0),
    expected("FLAG_FOR_APPROVAL", ["alaska-economy"], ["ECONOMY"], ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"],
             ["EXPORT_CONTROL_OFFICE", "NOT_NAMED", "SUPERVISOR_APPROVER", "UNIVERSITY_TRAVEL_OFFICE",
              "VICE_CHANCELLOR_BUSINESS_FINANCE"], ["PRE_TRIP_APPROVAL"],
             phrase="may require additional approval based on campus-specific procedures"),
    [NON_CONTINENTAL, REQUEST, INTL_DEFINED],
    "Hawaii is in the United States and needs no passport, so it is not International Travel (lines 53-55) and needs "
    "no Vice Chancellor approval. But lines 153-154: 'Non-continental United States travel may require additional "
    "approval based on campus-specific procedures.' The handbook gives no such procedure and names no approver, and "
    "the record holds only the supervisor's and financial approver's sign-offs. Whether the request is complete is "
    "open: hold the lowest coach fare, Alaska at $396.",
    flag_twins=["birch-lantern", "dune-sparrow"],
    ambiguity={"phrase": "may require additional approval based on campus-specific procedures",
               "readings": [("no further approval applies: the request approved by the supervisor and financial "
                            "approvers is complete, so book the lowest coach fare"),
                            ("a campus-specific approval may still be needed for travel outside the continental United "
                            "States, so hold the fare until it is confirmed")]},
    distractors=[THIRTY_DAYS])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for data in S:
        (OUT / f"{data['id']}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(S)} scenarios to {OUT}")


if __name__ == "__main__":
    main()
