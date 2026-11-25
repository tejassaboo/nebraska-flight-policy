"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only.

The first part is the original-handbook template's shared contract and is the same in every plugin made from
it. The HANDBOOK-SPECIFIC part in the middle is filled per handbook: the scenario ids, the closed lists of
approvers and sections, and the trip record; the shared inputs and outputs after it refer to those names.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output

# ---------------------------------------------------------------------------------------------------------
# SHARED (template): keep identical across plugins, except the agent task's id in Task.BOOK_FLIGHT.
# ---------------------------------------------------------------------------------------------------------


class Tool(Enum):
    BOOKING_REQUIREMENTS = "booking_requirements"
    GET_TRIP = "get_trip"
    SEARCH_FLIGHTS = "search_flights"
    SOLVE_BOOKING = "solve_booking"


class Task(Enum):
    BOOKING_REQUIREMENTS = "booking-requirements"
    SEARCH_FLIGHTS = "search-flights"
    BOOK_FLIGHT = "book-nebraska-flight"


class Decision(Enum):
    BOOK = "BOOK"
    REFUSE = "REFUSE"
    FLAG_FOR_APPROVAL = "FLAG_FOR_APPROVAL"


class Cabin(Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"
    NONE = "NONE"


class ReasonCode(Enum):
    """Why the decision was made. The list is shared by every handbook plugin, so it also holds reasons
    that a given handbook never uses."""

    LOWEST_FARE = "LOWEST_FARE"
    UPGRADE_NOT_ELIGIBLE = "UPGRADE_NOT_ELIGIBLE"
    CLIENT_REIMBURSABLE = "CLIENT_REIMBURSABLE"
    UPGRADE_WITHIN_FARE_MARGIN = "UPGRADE_WITHIN_FARE_MARGIN"
    MEDICAL_NEED = "MEDICAL_NEED"
    COST_SAVINGS = "COST_SAVINGS"
    NO_ECONOMY_SEATS_URGENT = "NO_ECONOMY_SEATS_URGENT"
    TRAVELER_PAYS_UPGRADE = "TRAVELER_PAYS_UPGRADE"
    LONG_FLIGHT_APPROVED = "LONG_FLIGHT_APPROVED"
    LONG_FLIGHT_CONDITION_NOT_MET = "LONG_FLIGHT_CONDITION_NOT_MET"
    PREMIUM_ECONOMY_ALLOWED = "PREMIUM_ECONOMY_ALLOWED"
    UPGRADE_COST_NOT_NOMINAL = "UPGRADE_COST_NOT_NOMINAL"
    ALTERNATE_ROUTE_WITHIN_MARGIN = "ALTERNATE_ROUTE_WITHIN_MARGIN"
    ALTERNATE_ROUTE_TOO_EXPENSIVE = "ALTERNATE_ROUTE_TOO_EXPENSIVE"
    LOYALTY_PROGRAM_PREFERENCE = "LOYALTY_PROGRAM_PREFERENCE"
    COMPANION_NOT_COVERED = "COMPANION_NOT_COVERED"
    PERSONAL_TRAVEL_NOT_COVERED = "PERSONAL_TRAVEL_NOT_COVERED"
    OUTSIDE_POLICY_SCOPE = "OUTSIDE_POLICY_SCOPE"
    NO_COMPLIANT_OFFER = "NO_COMPLIANT_OFFER"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    UNCLEAR_POLICY_TEXT = "UNCLEAR_POLICY_TEXT"
    ADVANCE_PURCHASE_TOO_LATE = "ADVANCE_PURCHASE_TOO_LATE"
    DISTANCE_BELOW_MINIMUM = "DISTANCE_BELOW_MINIMUM"
    DRIVING_EXPECTED = "DRIVING_EXPECTED"
    RAIL_PREFERRED = "RAIL_PREFERRED"
    REFUNDABLE_FARE_NOT_ALLOWED = "REFUNDABLE_FARE_NOT_ALLOWED"
    PREFERRED_CARRIER_REQUIRED = "PREFERRED_CARRIER_REQUIRED"
    CONNECTION_TOO_LONG = "CONNECTION_TOO_LONG"
    OVERNIGHT_STOP_REQUIRED = "OVERNIGHT_STOP_REQUIRED"
    NATIONAL_CARRIER_REQUIRED = "NATIONAL_CARRIER_REQUIRED"
    SENIOR_ROLE_ENTITLEMENT = "SENIOR_ROLE_ENTITLEMENT"
    INTERNATIONAL_LONG_FLIGHT = "INTERNATIONAL_LONG_FLIGHT"
    TRAVELLER_LIMIT_PER_FLIGHT = "TRAVELLER_LIMIT_PER_FLIGHT"
    # HANDBOOK-SPECIFIC reason codes go below this line; keep every shared one above.
    PRIVATE_AIRCRAFT_NOT_APPROVED = "PRIVATE_AIRCRAFT_NOT_APPROVED"
    TRAVEL_AGENCY_REQUIRED = "TRAVEL_AGENCY_REQUIRED"
    OUTSIDE_FARE_COMPARISON_NOT_MET = "OUTSIDE_FARE_COMPARISON_NOT_MET"
    PRE_TRIP_REQUEST_REQUIRED = "PRE_TRIP_REQUEST_REQUIRED"
    POLICY_EXEMPTION_DOCUMENTED = "POLICY_EXEMPTION_DOCUMENTED"
    ARRIVAL_NEEDED_FOR_BUSINESS = "ARRIVAL_NEEDED_FOR_BUSINESS"
    # Decoys: codes for rules of other handbooks that this one lacks, so the list hints at none of its own rules.
    WEEKEND_TRAVEL_HOME = "WEEKEND_TRAVEL_HOME"
    WEEKEND_TRIP_NOT_EARNED = "WEEKEND_TRIP_NOT_EARNED"
    NEXT_OF_KIN_TRAVEL = "NEXT_OF_KIN_TRAVEL"
    FLY_AMERICA_US_CARRIER_REQUIRED = "FLY_AMERICA_US_CARRIER_REQUIRED"
    OPEN_SKIES_AGREEMENT = "OPEN_SKIES_AGREEMENT"
    CREATIVE_TICKETING = "CREATIVE_TICKETING"
    DENIED_BOARDING_NOT_ALLOWED = "DENIED_BOARDING_NOT_ALLOWED"
    DOUBLE_BOOKING_PROHIBITED = "DOUBLE_BOOKING_PROHIBITED"
    SAME_CLASS_AS_CUSTOMER = "SAME_CLASS_AS_CUSTOMER"
    CANDIDATE_TRIP_NOT_COVERED = "CANDIDATE_TRIP_NOT_COVERED"


class TripType(Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"


class Topic(Enum):
    ALL = "ALL"
    FIELDS = "FIELDS"
    AIRPORTS = "AIRPORTS"


CODE = "An IATA airport code, e.g. JFK"


@dataclass
class Airport(Output):
    code: Annotated[str, CODE]
    name: Annotated[str, "The airport's name"]
    city: Annotated[str, "The city it serves"]
    country: Annotated[str, "Its country, as an ISO code"]


@dataclass
class Segment(Output):
    flight_number: Annotated[str, "The airline's flight number, e.g. BA 117"]
    origin: Annotated[str, CODE]
    destination: Annotated[str, CODE]
    depart_local: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, local time at that airport"]
    arrive_local: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, local time at that airport"]
    depart_utc: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, UTC"]
    arrive_utc: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, UTC"]
    scheduled_minutes: Annotated[int, "Its scheduled time from departure to arrival, in minutes"]


@dataclass
class Offer(Output):
    offer_id: Annotated[str, "The offer's id, to submit when booking or holding it"]
    carrier: Annotated[str, "The airline"]
    trip_type: Annotated[TripType, "ONE_WAY, or ROUND_TRIP when the fare covers the flights out and back"]
    cabin: Annotated[Cabin, "The cabin sold on every flight of the offer"]
    fare_cents: Annotated[int, "The whole fare for one passenger, in cents of the search's currency"]
    seats_available: Annotated[bool, "False when this cabin is sold out on these flights: it is listed but cannot be bought"]
    refundable: Annotated[bool, "Whether the fare can be refunded or changed without a fee"]
    stops: Annotated[int, "Connections on the way out; zero for a nonstop"]
    segments: Annotated[list[Segment], "The flights out, in order"]
    layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights out"]
    stopover_nights: Annotated[list[bool], "Per connection out: true when it is a ticketed stopover with a hotel night booked"]
    flying_minutes: Annotated[int, "The flights' scheduled minutes out added together, ground time left out"]
    elapsed_minutes: Annotated[int, "Minutes from the first departure out to the last arrival, ground time included"]
    return_segments: Annotated[list[Segment], "For a round trip, the flights back, in order; empty otherwise"]
    return_layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights back"]
    return_stopover_nights: Annotated[list[bool], "Per connection back: true for a ticketed stopover with a hotel night"]
    return_flying_minutes: Annotated[int, "The flights' scheduled minutes back added together; zero one way"]
    return_elapsed_minutes: Annotated[int, "Minutes from the first departure back to the last arrival; zero one way"]


# ---------------------------------------------------------------------------------------------------------
# HANDBOOK-SPECIFIC: University of Nebraska Travel Policy (effective 2018, last revised March 7, 2019).
# ---------------------------------------------------------------------------------------------------------


class Scenario(Enum):
    BIRCH_LANTERN = "birch-lantern"
    COBALT_MEADOW = "cobalt-meadow"
    DUNE_SPARROW = "dune-sparrow"
    EMBER_THICKET = "ember-thicket"
    FERN_GABLE = "fern-gable"
    GARNET_REED = "garnet-reed"
    HERON_SLATE = "heron-slate"
    IRIS_COPPER = "iris-copper"
    JUNIPER_WOLD = "juniper-wold"
    KESTREL_MOOR = "kestrel-moor"
    LINDEN_SHOAL = "linden-shoal"
    MAPLE_CINDER = "maple-cinder"
    NUTMEG_RIDGE = "nutmeg-ridge"
    OPAL_FJORD = "opal-fjord"
    PEWTER_GLEN = "pewter-glen"
    QUARTZ_BRAMBLE = "quartz-bramble"
    RUSSET_DELL = "russet-dell"
    SORREL_PIKE = "sorrel-pike"
    TANSY_BLUFF = "tansy-bluff"
    UMBER_LOCH = "umber-loch"
    VETCH_HOLLOW = "vetch-hollow"
    WILLOW_CRAG = "willow-crag"
    YARROW_FLINT = "yarrow-flint"
    ZINNIA_MARSH = "zinnia-marsh"


class Approver(Enum):
    """Roles that may sign off. NONE: the decision relies on no one's sign-off, given or awaited (one for
    something else may be on file). NOT_NAMED: one is needed, but the handbook names no role."""

    NONE = "NONE"
    NOT_NAMED = "NOT_NAMED"
    SUPERVISOR_APPROVER = "SUPERVISOR_APPROVER"
    FINANCIAL_APPROVER = "FINANCIAL_APPROVER"
    VICE_CHANCELLOR_BUSINESS_FINANCE = "VICE_CHANCELLOR_BUSINESS_FINANCE"
    UNIVERSITY_TRAVEL_OFFICE = "UNIVERSITY_TRAVEL_OFFICE"
    ADA_COORDINATOR = "ADA_COORDINATOR"
    EXPORT_CONTROL_OFFICE = "EXPORT_CONTROL_OFFICE"
    PURCHASING_CARD_OFFICE = "PURCHASING_CARD_OFFICE"
    DEAN = "DEAN"
    DEPARTMENT_CHAIR = "DEPARTMENT_CHAIR"
    PROVOST = "PROVOST"
    CHIEF_FINANCIAL_OFFICER = "CHIEF_FINANCIAL_OFFICER"
    TRAVEL_MANAGER = "TRAVEL_MANAGER"


class Clause(Enum):
    """The handbook's sections, by heading."""

    SCOPE = "SCOPE"
    POLICY_STATEMENT = "POLICY_STATEMENT"
    DEFINITIONS = "DEFINITIONS"
    UNIT_POLICIES = "UNIT_POLICIES"
    NON_UNIVERSITY_PERSONNEL = "NON_UNIVERSITY_PERSONNEL"
    COMPLIANCE_AND_EXEMPTIONS = "COMPLIANCE_AND_EXEMPTIONS"
    PRE_TRIP_APPROVAL = "PRE_TRIP_APPROVAL"
    MOST_ECONOMICAL_RATES = "MOST_ECONOMICAL_RATES"
    PERSONAL_TRAVEL = "PERSONAL_TRAVEL"
    BLANKET_AUTHORIZATION = "BLANKET_AUTHORIZATION"
    PAID_DIRECTLY = "PAID_DIRECTLY"
    PAID_BY_EMPLOYEE = "PAID_BY_EMPLOYEE"
    PURCHASING_CARD = "PURCHASING_CARD"
    COMMERCIAL_AIR = "COMMERCIAL_AIR"
    AIR_BOOKING = "AIR_BOOKING"
    UPGRADES = "UPGRADES"
    CANCELLATIONS = "CANCELLATIONS"
    RENTAL_CARS = "RENTAL_CARS"
    OTHER_FORMS_OF_TRAVEL = "OTHER_FORMS_OF_TRAVEL"
    LODGING = "LODGING"
    MEAL_ALLOWANCES = "MEAL_ALLOWANCES"
    EXPENSE_DEADLINE = "EXPENSE_DEADLINE"
    INTERNATIONAL_TRAVEL = "INTERNATIONAL_TRAVEL"
    EXECUTIVE_MEMORANDUM = "EXECUTIVE_MEMORANDUM"
    EXPORT_CONTROL = "EXPORT_CONTROL"
    TRAVEL_WITH_STUDENTS = "TRAVEL_WITH_STUDENTS"
    STUDENT_INSURANCE = "STUDENT_INSURANCE"
    APPENDIX_RECEIPTS = "APPENDIX_RECEIPTS"


class Passenger(Enum):
    EMPLOYEE = "EMPLOYEE"
    CONTRACTED_SPEAKER = "CONTRACTED_SPEAKER"
    COMPANION = "COMPANION"


class Purpose(Enum):
    CONFERENCE = "CONFERENCE"
    RESEARCH = "RESEARCH"
    MEETING = "MEETING"
    WORKSHOP = "WORKSHOP"
    HEARING = "HEARING"
    EXTENSION_PROGRAM = "EXTENSION_PROGRAM"
    PERSONAL = "PERSONAL"


class TravelMode(Enum):
    AIRLINE = "AIRLINE"
    CHARTERED_PLANE = "CHARTERED_PLANE"


class RequestKind(Enum):
    SINGLE_TRIP = "SINGLE_TRIP"
    BLANKET = "BLANKET"


class SignOffSubject(Enum):
    TRIP_REQUEST = "TRIP_REQUEST"
    TRAVEL_ABROAD = "TRAVEL_ABROAD"
    ACCOMMODATION = "ACCOMMODATION"


@dataclass
class TripRequest(Output):
    kind: Annotated[RequestKind, "SINGLE_TRIP: filed for this trip alone; BLANKET: one filing meant to cover repeated trips for one purpose over a year"]
    submitted_on: Annotated[str, "The day it was filed in the university's expense tool, YYYY-MM-DD"]
    covers: Annotated[str, "What the filing describes, in plain words"]


@dataclass
class SignOff(Output):
    role: Annotated[Approver, "The signer's role"]
    name: Annotated[str, "Their name"]
    subject: Annotated[SignOffSubject, "What they signed: the trip request, the trip's travel abroad, or an accommodation of a disability"]
    covers: Annotated[str, "What the sign-off says, in plain words"]
    given_on: Annotated[str, "The day it was given, YYYY-MM-DD"]


@dataclass
class OutsideFare(Output):
    source: Annotated[str, "Where the traveller saw it: an airline's own site or a booking site"]
    flight_number: Annotated[str, "Its first flight, as search_flights names flights"]
    fare_cents: Annotated[int, "The price shown there, every fee included, in cents of the search's currency"]
    found_on: Annotated[str, "The day the traveller looked it up, YYYY-MM-DD"]


@dataclass
class Trip(Output):
    traveller_name: Annotated[str, "Who flies"]
    traveller_title: Annotated[str, "Their job title, or how they are linked to the university"]
    passenger: Annotated[Passenger, "Who the person flying is: a university employee, a speaker under contract with the university, or someone going along with an employee"]
    accompanies: Annotated[str, "The employee this person goes with, when the person flying is not on university business; empty otherwise"]
    campus: Annotated[str, "The traveller's campus or work location, or the hosting unit for a speaker"]
    origin: Annotated[Airport, "Where the flight leaves from"]
    destination: Annotated[Airport, "Where it goes"]
    destination_needs_passport: Annotated[bool, "Whether the traveller needs a passport to enter the destination"]
    travel_date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport"]
    return_date: Annotated[str, "For a round trip bought as one fare, the day to fly back, YYYY-MM-DD; empty for one way"]
    booking_date: Annotated[str, "Today in this world, the day the ticket is bought, YYYY-MM-DD"]
    purpose: Annotated[str, "Why the trip is made, in plain words"]
    purpose_kind: Annotated[Purpose, "The kind of trip"]
    must_arrive_by: Annotated[str, "The latest landing that still lets the work start on time, YYYY-MM-DD HH:MM local at the destination; empty when no landing time matters"]
    requested_cabin: Annotated[Cabin, "The cabin the traveller asks for"]
    traveller_pays_upgrade: Annotated[bool, "Whether the traveller offers to pay, out of pocket, for a better cabin than the one the university would buy"]
    requested_mode: Annotated[TravelMode, "AIRLINE for a scheduled airline flight; CHARTERED_PLANE when the traveller asks for a chartered plane"]
    wants_to_book_outside: Annotated[bool, "Whether the traveller asks to buy the ticket themselves, away from the university's agency whose fares search_flights lists"]
    outside_fares: Annotated[list[OutsideFare], "Fares the traveller found elsewhere; empty when none"]
    trip_request: Annotated[TripRequest, "The request for this travel filed before booking"]
    sign_offs: Annotated[list[SignOff], "Sign-offs already on file, each given before today"]


# ---------------------------------------------------------------------------------------------------------
# SHARED (template), continued: the tools' and tasks' inputs and outputs.
# ---------------------------------------------------------------------------------------------------------


@dataclass
class TaskInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    request: Annotated[str, "The traveller's request, in their own words"]


@dataclass
class TripInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id, as the task input gives it"]


@dataclass
class TripOutput(Output):
    scenario: Annotated[Scenario, "The case id"]
    request: Annotated[str, "The traveller's request, in their own words"]
    trip: Annotated[Trip, "The trip record behind the request"]


@dataclass
class SearchInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    origin: Annotated[str, "The airport to leave from: An IATA airport code, e.g. JFK"]
    destination: Annotated[str, "The airport to fly to: An IATA airport code, e.g. JFK"]
    date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport, on or after the booking date"]
    return_date: Annotated[str, "For round-trip fares, the day to fly back, YYYY-MM-DD, local at the destination; empty for one way"]


@dataclass
class SearchOutput(Output):
    note: Annotated[str, "Where the offers come from, and a word when this case lists none for the search"]
    currency: Annotated[str, "The currency of every fare, as an ISO code"]
    offers: Annotated[list[Offer], "Every offer leaving on that local date, in departure order"]


@dataclass
class BookingOutput(Output):
    decision: Annotated[
        Decision,
        "BOOK: buy offer_id now. REFUSE: buy nothing, because the organisation buys no ticket at all for this request. "
        "FLAG_FOR_APPROVAL: hold offer_id and buy nothing yet, because someone must approve it first or "
        "the handbook's words leave the answer open",
    ]
    offer_id: Annotated[str, "The offer bought or held, exactly as search_flights listed it; empty when refusing"]
    cabin: Annotated[Cabin, "That offer's cabin; NONE when refusing"]
    reason_code: Annotated[ReasonCode, "Why, from the closed list"]
    approver: Annotated[
        Approver,
        "The role whose sign-off this decision relies on, whether already on file or still awaited; NONE when "
        "this decision relies on no one's sign-off, even if a sign-off for something else is on file; NOT_NAMED "
        "when a sign-off is needed but the handbook names no role",
    ]
    clause: Annotated[Clause, "The handbook section the decision rests on"]


@dataclass
class SolveOutput(Output):
    trip: Annotated[Trip, "The trip record"]
    offers: Annotated[list[Offer], "Every offer on the trip's route and date"]
    decision: Annotated[Decision, "The correct decision"]
    offer_ids: Annotated[list[str], "Every offer id that is a correct choice; empty when refusing"]
    cabins: Annotated[list[Cabin], "Every correct cabin"]
    reason_codes: Annotated[list[ReasonCode], "Every accepted reason"]
    approvers: Annotated[list[Approver], "Every accepted approver"]
    clauses: Annotated[list[Clause], "Every accepted section"]
    unclear_phrase: Annotated[str, "For a hold over unclear words, those words; empty otherwise"]
    explanation: Annotated[str, "How the answer key reached the answer"]


@dataclass
class FieldHelp(Output):
    name: Annotated[str, "The trip record field's name"]
    kind: Annotated[str, "Its type"]
    description: Annotated[str, "What it means"]


@dataclass
class RequirementsInput(Output):
    topic: Annotated[Topic, "ALL for everything, FIELDS for the trip record's fields, AIRPORTS for the airport list"]


@dataclass
class RequirementsOutput(Output):
    fields: Annotated[list[FieldHelp], "The trip record's fields; empty for AIRPORTS"]
    conventions: Annotated[list[str], "How times, dates, fares and seats work in this world; empty for AIRPORTS"]
    airports: Annotated[list[Airport], "The airports the simulated world knows; empty for FIELDS"]


TOOLS = {
    Tool.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Tool.GET_TRIP: (TripInput, TripOutput),
    Tool.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Tool.SOLVE_BOOKING: (TaskInput, SolveOutput),
}
TASKS = {
    Task.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Task.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Task.BOOK_FLIGHT: (TaskInput, BookingOutput),
}
