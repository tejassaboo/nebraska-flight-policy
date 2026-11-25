"""The answer key's rules for the University of Nebraska Travel Policy (effective 2018, last revised March 7,
2019), as exact integer code. Byte-identical in src/plugin/rules.py and verifier/rules.py; it imports only
modules a verifier may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an
answer open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each
unclear phrase at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a
new scenario cannot fall silently into untested logic.

No duration hook. The handbook gives no flight-length threshold at all: it gives no premium cabin for long
flights (the fare is capped at the coach or main cabin price, lines 237-239), so DURATION_RULES is empty and
over() raises.

The handbook's flight rules are process rules:
- lines 136-146: a Pre-Trip Request before each trip, approved by the Supervisor Approver and the Financial
  Approver, before any booking; a Blanket Travel Authorization covers only travel within city limits, a
  100-mile radius or State limits (lines 172-181);
- lines 148-154 and 449-454: International Travel (defined at lines 53-55: outside the United States and its
  territories, or any destination that needs a passport) needs the Vice Chancellor of Business and
  Finance's approval; submitting 30 days ahead is advice ("well-advised", "should"), not a ban;
  non-continental United States travel "may require additional approval based on campus-specific
  procedures", which the handbook does not give (an unclear-text hold);
- lines 156-158 and 316-321: privately owned or chartered planes need the Vice Chancellor's approval;
  lines 208-211: commercial airlines are expected;
- lines 222-235: flights through the University-contracted travel management company (the agency whose
  fares search_flights lists); international flights outside it only when the flights are not available
  through it; domestic flights outside it only with proof of a comparable, less expensive fare, all fees
  included, compared on the same day;
- lines 237-239: a ticket not above the coach or main cabin price at purchase; a ticket that is not the
  lowest listed price needs a brief explanation; lines 159-162: the most economical means that meet the
  approved goals of the trip (here: the trip record's latest landing time);
- lines 241-247: an upgrade is the traveller's own, arranged afterwards as a ticket exchange with the agency;
- lines 118-123: exemptions only with documentation such as an ADA accommodation plan, the campus ADA/504
  coordinator's written description sent to the University Travel Office;
- lines 102-106: non-University personnel (speakers under contract) follow the policy too;
- lines 26-28, 163-170 and the appendix (spouse/companion expenses not reimbursable): the University pays for
  University business only.

Approvers (SYNC_NOTES.md rule 4'): a booking whose sign-offs are already on file accepts each of those roles
and NONE; a sign-off on file that the decision does not use is accepted beside NONE (rule 4(b)); a hold
accepts only the role(s) it awaits (NOT_NAMED where the handbook names none), never NONE.
"""

from contract import (
    Approver,
    Cabin,
    Clause,
    Decision,
    Passenger,
    Purpose,
    ReasonCode,
    RequestKind,
    SignOffSubject,
    TravelMode,
)

HANDBOOK = "University of Nebraska Travel Policy, effective 2018, last revised March 7, 2019"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.SCOPE: "Scope and Reason for the Policy",
    Clause.POLICY_STATEMENT: "Policy Statement",
    Clause.DEFINITIONS: "Definitions",
    Clause.UNIT_POLICIES: "Campus, College or Unit Policies",
    Clause.NON_UNIVERSITY_PERSONNEL: "Non-University Personnel",
    Clause.COMPLIANCE_AND_EXEMPTIONS: "Compliance and Exemptions",
    Clause.PRE_TRIP_APPROVAL: "Pre-Trip Approval",
    Clause.MOST_ECONOMICAL_RATES: "Most Economical Rates",
    Clause.PERSONAL_TRAVEL: "Personal Travel",
    Clause.BLANKET_AUTHORIZATION: "Blanket Travel Authorization",
    Clause.PAID_DIRECTLY: "Expenses Paid Directly by the University",
    Clause.PAID_BY_EMPLOYEE: "Expenses Paid by Employee",
    Clause.PURCHASING_CARD: "Purchasing Card",
    Clause.COMMERCIAL_AIR: "Commercial Air",
    Clause.AIR_BOOKING: "Booking",
    Clause.UPGRADES: "Upgrades",
    Clause.CANCELLATIONS: "Cancellations",
    Clause.RENTAL_CARS: "Rental Cars",
    Clause.OTHER_FORMS_OF_TRAVEL: "Other Forms of Travel",
    Clause.LODGING: "Lodging",
    Clause.MEAL_ALLOWANCES: "Meal Allowances",
    Clause.EXPENSE_DEADLINE: "Travel Expense Deadline",
    Clause.INTERNATIONAL_TRAVEL: "International Travel",
    Clause.EXECUTIVE_MEMORANDUM: "Executive Memorandum No. 25",
    Clause.EXPORT_CONTROL: "Export Control",
    Clause.TRAVEL_WITH_STUDENTS: "Travel with Students",
    Clause.STUDENT_INSURANCE: "Student Travel Insurance",
    Clause.APPENDIX_RECEIPTS: "APPENDIX A",
}

# The handbook's duration thresholds: none (no flight length changes the cabin or anything else).
DURATION_RULES = ()

# Handbook-specific conventions shown by booking_requirements, beyond the template's (none here).
CONVENTIONS = ()

# Lines 53-55: International Travel is "travel outside of the United States and its territories or travel to
# any destination that requires a passport". The world's US airports are in country "US"; the territories'
# (Puerto Rico, Guam) have their own codes and no scenario goes there.
HOME_COUNTRY = "US"
# Lines 149-154: "non-continental United States travel". Hawaii and Alaska airports of the shared world.
NON_CONTINENTAL = ("HNL", "ANC")

UNCLEAR_REASONS = [ReasonCode.UNCLEAR_POLICY_TEXT, ReasonCode.APPROVAL_REQUIRED]
CAMPUS_PHRASE = "may require additional approval based on campus-specific procedures"

TRIP_APPROVERS = [Approver.SUPERVISOR_APPROVER, Approver.FINANCIAL_APPROVER]
VICE_CHANCELLOR = Approver.VICE_CHANCELLOR_BUSINESS_FINANCE
LOWEST_CLAUSES = [Clause.AIR_BOOKING, Clause.MOST_ECONOMICAL_RATES, Clause.COMMERCIAL_AIR, Clause.PRE_TRIP_APPROVAL]
CABIN_CLAUSES = [Clause.AIR_BOOKING, Clause.UPGRADES]
TIMING_CLAUSES = [Clause.MOST_ECONOMICAL_RATES, Clause.AIR_BOOKING, Clause.COMMERCIAL_AIR]
AGENCY_CLAUSES = [Clause.AIR_BOOKING, Clause.APPENDIX_RECEIPTS]


def over(rule, offer):
    """The duration hook: this handbook has no duration rule, so every name is unknown."""
    raise ValueError(f"unknown duration rule {rule!r}: the handbook has no flight-length threshold")


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def cheapest(offers):
    if not offers:
        return []
    low = min(offer.fare_cents for offer in offers)
    return [offer for offer in offers if offer.fare_cents == low]


def signed(trip, subject):
    return [record.role for record in trip.sign_offs if record.subject == subject]


def on_route(trip, offers):
    return [offer for offer in offers if offer.segments[0].origin == trip.origin.code
            and offer.segments[-1].destination == trip.destination.code
            and offer.segments[0].depart_local[:10] == trip.travel_date]


def in_time(trip, offer):
    """Whether the offer lands by the trip record's latest useful landing (local time at the destination)."""
    return not trip.must_arrive_by or offer.segments[-1].arrive_local <= trip.must_arrive_by


def coach(trip, seated):
    """Lines 237-239 and 159-162: the lowest listed coach fare among the flights that meet the trip's goals
    (land in time). Returns the offers, their reasons and a note."""
    economy = [offer for offer in seated if offer.cabin == Cabin.ECONOMY]
    if not economy:
        raise ValueError("no economy seat can be bought: not modelled")
    timely = [offer for offer in economy if in_time(trip, offer)]
    if not timely:
        raise ValueError("no economy flight lands in time: not modelled")
    low, best = cheapest(economy), cheapest(timely)
    if len(best) != 1:
        raise ValueError("tied lowest coach fares are not modelled")
    if low == best:
        return best, [ReasonCode.LOWEST_FARE], [], "lines 237-239: the lowest listed coach fare"
    return (best, [ReasonCode.LOWEST_FARE, ReasonCode.ARRIVAL_NEEDED_FOR_BUSINESS], TIMING_CLAUSES,
            (f"lines 160-162: the cheapest coach fare ({low[0].fare_cents} cents) lands after "
            f"{trip.must_arrive_by}, too late for the trip's purpose; the most economical flight that meets the "
            f"trip's goals is the {best[0].fare_cents}-cent fare, and lines 238-239 only ask for a brief "
            "explanation of a fare that is not the lowest listed price"))


def international(trip):
    return trip.destination.country != HOME_COUNTRY or trip.destination_needs_passport


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers on its searches: the decision, and every accepted offer id,
    cabin, reason, approver and section. ``hidden`` (the scenario's answer_key_inputs) is unused by this
    handbook."""
    if hidden:
        raise ValueError("this handbook's scenarios carry no answer_key_inputs")
    if trip.return_date:
        raise ValueError("a round-trip ticket is not modelled")
    if trip.origin.country != HOME_COUNTRY:
        raise ValueError("a trip that starts abroad is not modelled")
    request_roles = signed(trip, SignOffSubject.TRIP_REQUEST)
    if sorted(request_roles, key=lambda role: role.value) != sorted(TRIP_APPROVERS, key=lambda role: role.value):
        raise ValueError("every case holds the request's supervisor and financial approvals (lines 143-146)")
    unused = [Approver.NONE, *request_roles]
    if trip.passenger == Passenger.COMPANION:
        return answer(Decision.REFUSE, [], [ReasonCode.COMPANION_NOT_COVERED, ReasonCode.PERSONAL_TRAVEL_NOT_COVERED,
                                            ReasonCode.OUTSIDE_POLICY_SCOPE],
                      unused, [Clause.POLICY_STATEMENT, Clause.PERSONAL_TRAVEL, Clause.APPENDIX_RECEIPTS, Clause.SCOPE,
                               Clause.DEFINITIONS],
                      "Lines 26-28: the University pays for travel incurred in the performance of University business; "
                      "lines 163-170: only the business portion is paid; the appendix lists spouse/companion expenses "
                      "as not reimbursable. The companion's flight is not University business: no ticket.")
    if trip.purpose_kind == Purpose.PERSONAL:
        return answer(Decision.REFUSE, [], [ReasonCode.PERSONAL_TRAVEL_NOT_COVERED, ReasonCode.OUTSIDE_POLICY_SCOPE],
                      unused, [Clause.PERSONAL_TRAVEL, Clause.POLICY_STATEMENT, Clause.SCOPE, Clause.DEFINITIONS],
                      "Lines 163-170: personal travel during Travel Status is the traveller's; the University pays only "
                      "the University business portion (lines 26-28). This flight is wholly personal: no ticket.")
    seated = [offer for offer in on_route(trip, offers) if offer.seats_available]
    if trip.trip_request.kind == RequestKind.BLANKET:
        return blanket(trip, seated)
    if international(trip):
        if VICE_CHANCELLOR not in signed(trip, SignOffSubject.TRAVEL_ABROAD):
            held = coach(trip, seated)[0]
            return answer(Decision.FLAG_FOR_APPROVAL, held,
                          [ReasonCode.APPROVAL_REQUIRED, ReasonCode.PRE_TRIP_REQUEST_REQUIRED], [VICE_CHANCELLOR],
                          [Clause.PRE_TRIP_APPROVAL, Clause.INTERNATIONAL_TRAVEL, Clause.DEFINITIONS],
                          "Lines 53-55: travel outside the United States, or to a destination that needs a passport, is "
                          "International Travel; lines 151-153: it needs additional approval from the Vice Chancellor of "
                          "Business and Finance or their designee, and lines 144-145 require the approved request before "
                          "any booking. Hold the lowest coach fare for the Vice Chancellor.")
        roles = [Approver.NONE, *request_roles, VICE_CHANCELLOR]
        extra = [Clause.INTERNATIONAL_TRAVEL]
    elif trip.destination.code in NON_CONTINENTAL:
        held = coach(trip, seated)[0]
        return answer(Decision.FLAG_FOR_APPROVAL, held, UNCLEAR_REASONS,
                      # Lines 148-149 name supervisors, export control offices, the University Travel Office
                      # and other administration as reviewers of non-continental travel.
                      [Approver.NOT_NAMED, Approver.UNIVERSITY_TRAVEL_OFFICE, VICE_CHANCELLOR,
                       Approver.SUPERVISOR_APPROVER, Approver.EXPORT_CONTROL_OFFICE],
                      [Clause.PRE_TRIP_APPROVAL],
                      "Lines 153-154: non-continental United States travel 'may require additional approval based on "
                      "campus-specific procedures'; the handbook does not give those procedures or name the approver, "
                      "and the record shows only the supervisor's and financial approver's sign-offs. Whether the "
                      "request is complete is open: hold the lowest coach fare.", phrase=CAMPUS_PHRASE)
    else:
        roles = [Approver.NONE, *request_roles]
        extra = []
    return booking(trip, seated, roles, extra)


def blanket(trip, seated):
    """Lines 172-181: a Blanket Travel Authorization covers only travel within city limits, a 100-mile radius
    of the campus or State limits; other travel goes through the standard, individual request (lines
    136-146), which needs the supervisor's and financial approver's approval before any booking."""
    if trip.origin.country != HOME_COUNTRY or international(trip):
        raise ValueError("a blanket authorization for travel abroad is not modelled")
    held = coach(trip, seated)[0]
    return answer(Decision.FLAG_FOR_APPROVAL, held, [ReasonCode.APPROVAL_REQUIRED, ReasonCode.PRE_TRIP_REQUEST_REQUIRED],
                  TRIP_APPROVERS, [Clause.BLANKET_AUTHORIZATION, Clause.PRE_TRIP_APPROVAL],
                  "Lines 177-181: a Blanket Travel Authorization covers travel within city limits, a 100-mile radius or "
                  "State limits; a flight out of the state must be requested through the individual trip process, and "
                  "lines 143-146 need its supervisor and financial approvals before any booking. Hold the lowest coach "
                  "fare for those approvals.")


def booking(trip, seated, roles, extra):
    """A trip whose request (and travel-abroad approval, when needed) is on file."""
    if trip.requested_mode == TravelMode.CHARTERED_PLANE:
        if trip.requested_cabin != Cabin.ECONOMY or trip.wants_to_book_outside:
            raise ValueError("a charter request beside another request is not modelled")
        chosen, _, clauses, note = coach(trip, seated)
        # Lines 316-318 also make the charter wait on an affirmation that no more economical means exists, and
        # lines 212-213 pay only up to the most economical option: a reader may give that ground instead.
        return answer(Decision.BOOK, chosen, [ReasonCode.PRIVATE_AIRCRAFT_NOT_APPROVED, ReasonCode.LOWEST_FARE], roles,
                      [Clause.PRE_TRIP_APPROVAL, Clause.OTHER_FORMS_OF_TRAVEL, Clause.COMMERCIAL_AIR,
                       Clause.MOST_ECONOMICAL_RATES, *clauses, *extra],
                      "Lines 156-158 and 314-320: a chartered plane needs the Vice Chancellor's additional approval, "
                      "which is not on file; lines 208-211: commercial airlines are expected, and the traveller asked "
                      f"for an airline flight otherwise; {note}.")
    if trip.wants_to_book_outside:
        return outside(trip, seated, roles, extra)
    if trip.outside_fares:
        raise ValueError("an outside fare the traveller does not ask to use is not modelled")
    accommodation = signed(trip, SignOffSubject.ACCOMMODATION)
    if accommodation and accommodation != [Approver.ADA_COORDINATOR]:
        raise ValueError("an accommodation not signed by the ADA/504 coordinator alone is not modelled")
    if trip.requested_cabin == Cabin.ECONOMY:
        if trip.traveller_pays_upgrade:
            raise ValueError("a paid upgrade on an economy request is not modelled")
        chosen, reasons, clauses, note = coach(trip, seated)
        # An accommodation on file that this booking does not use is accepted beside NONE (rule 4(b)).
        return answer(Decision.BOOK, chosen, reasons, [*roles, *accommodation], [*LOWEST_CLAUSES, *clauses, *extra],
                      f"{note}; lines 143-146: the request is approved before booking.")
    wanted = [offer for offer in seated if offer.cabin == trip.requested_cabin and in_time(trip, offer)]
    if accommodation:
        better = cheapest(wanted)
        if len(better) != 1 or trip.traveller_pays_upgrade:
            raise ValueError("an accommodated cabin with tied or no fares, or paid by the traveller, is not modelled")
        return answer(Decision.BOOK, better, [ReasonCode.POLICY_EXEMPTION_DOCUMENTED, ReasonCode.MEDICAL_NEED],
                      [*roles, Approver.ADA_COORDINATOR, Approver.UNIVERSITY_TRAVEL_OFFICE],
                      # Line 162 counts special needs in the most economic option; the approved request
                      # incorporates the accommodation (lines 122-123, 143-146).
                      [Clause.COMPLIANCE_AND_EXEMPTIONS, Clause.MOST_ECONOMICAL_RATES, Clause.PRE_TRIP_APPROVAL,
                       *extra],
                      "Lines 118-123: an exemption documented by an ADA accommodation plan, whose written description "
                      "the campus ADA/504 coordinator gave the University Travel Office, is part of the approved "
                      "request: the cheapest fare in the accommodated cabin.")
    chosen, reasons, clauses, note = coach(trip, seated)
    if clauses:
        raise ValueError("a better cabin beside a late cheapest coach fare is not modelled")
    if trip.traveller_pays_upgrade:
        return answer(Decision.BOOK, chosen, [ReasonCode.TRAVELER_PAYS_UPGRADE, ReasonCode.UPGRADE_NOT_ELIGIBLE], roles,
                      [*CABIN_CLAUSES, *extra],
                      "Lines 237-238: the ticket may not exceed the coach or main cabin price; lines 241-244: an upgrade "
                      "is the traveller's own, arranged as a ticket exchange with the agency and paid by them. The "
                      f"University buys the coach ticket: {note}.")
    within = [offer for offer in wanted if offer.fare_cents <= chosen[0].fare_cents]
    if within:
        if len(within) != 1:
            raise ValueError("several better-cabin fares within the coach price are not modelled")
        return answer(Decision.BOOK, within, [ReasonCode.PREMIUM_ECONOMY_ALLOWED, ReasonCode.LOWEST_FARE,
                                              ReasonCode.UPGRADE_WITHIN_FARE_MARGIN], roles,
                      [*CABIN_CLAUSES, Clause.MOST_ECONOMICAL_RATES, *extra],
                      f"Lines 237-238: the requested cabin's fare ({within[0].fare_cents} cents) does not exceed the "
                      "coach fare at purchase, which is also the lowest listed price: the traveller's choice is allowed.")
    clauses = [*CABIN_CLAUSES, *extra]
    why = "Lines 237-238: the ticket may not exceed the coach or main cabin price at purchase"
    if trip.passenger == Passenger.CONTRACTED_SPEAKER:
        clauses.append(Clause.NON_UNIVERSITY_PERSONNEL)
        why = ("Lines 102-106: a speaker under contract with the University is expected to comply with the policy; " +
               why[0].lower() + why[1:])
    elif trip.passenger != Passenger.EMPLOYEE:
        raise ValueError("this passenger is not modelled")
    # Lines 241-244 (accepted as UPGRADES) make an upgrade the traveller's own: a reader may give that ground.
    return answer(Decision.BOOK, chosen, [ReasonCode.UPGRADE_NOT_ELIGIBLE, ReasonCode.TRAVELER_PAYS_UPGRADE], roles,
                  clauses,
                  f"{why}, and the requested cabin's cheapest fare exceeds it; {note}.")


def outside(trip, seated, roles, extra):
    """Lines 222-235: the traveller asks to buy the ticket away from the agency."""
    if trip.requested_cabin != Cabin.ECONOMY or len(trip.outside_fares) != 1:
        raise ValueError("an outside purchase beside a cabin request, or without one outside fare, is not modelled")
    found = trip.outside_fares[0]
    chosen, reasons, clauses, note = coach(trip, seated)
    if clauses or reasons != [ReasonCode.LOWEST_FARE]:
        raise ValueError("an outside purchase beside a late cheapest coach fare is not modelled")
    listed = [offer for offer in seated if offer.segments[0].flight_number == found.flight_number]
    if not listed:
        raise ValueError("an outside fare for a flight the agency does not list is not modelled")
    if international(trip):
        return answer(Decision.BOOK, chosen, [ReasonCode.TRAVEL_AGENCY_REQUIRED], roles, [*AGENCY_CLAUSES, *extra],
                      "Lines 222-225: international flights are booked through the University-contracted travel "
                      "management company, and outside it only when the required flights are not available through "
                      f"it; the agency lists {found.flight_number}, so the University books it there: {note}.")
    same_day = found.found_on == trip.booking_date
    cheaper = found.fare_cents < min(offer.fare_cents for offer in listed)
    if same_day and cheaper:
        raise ValueError("a qualifying outside purchase (the traveller books it) is not modelled")
    return answer(Decision.BOOK, chosen, [ReasonCode.OUTSIDE_FARE_COMPARISON_NOT_MET, ReasonCode.TRAVEL_AGENCY_REQUIRED],
                  roles, [*AGENCY_CLAUSES, *extra],
                  "Lines 228-234: buying domestic air outside the agency needs proof of a comparable, less expensive "
                  f"fare with all fees, compared on the same day; the outside fare was found on {found.found_on}, not "
                  f"on the booking day {trip.booking_date}, so the University books through the agency: {note}.")
