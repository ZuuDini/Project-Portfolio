# Feasibility: automated OpenTable reservations from a voice-agent capture loop

**Date:** 2026-10-22
**Question:** What would it take to connect directly into OpenTable and import reservations automatically from a voice-agent capture loop (lead lands in Airtable or a Google Sheet with name, number, time, notes)? What do we need to implement, how do we turn captured data into a real OpenTable reservation, and how practical is it?
**Context:** Written for the builder of Yapper AI (Vapi → webhook → n8n → Airtable, plus a FastAPI webhook service on Railway with a pytest suite). This report consolidates five parallel research threads: OpenTable's official API program, how voice vendors integrate today, alternative platforms, a technical pipeline design, and a business and legal practicality review.

**Labels:** [C] confirmed from a primary source (OpenTable docs, contracts, press releases, platform docs). [V] vendor or third-party claim. [I] inference. [U] unknown.

---

## 1. Executive answer

There is exactly one sanctioned way to write a reservation into a restaurant's OpenTable book from an outside system: OpenTable's partner-only **In-House Booking API, which OpenTable itself calls the Voice AI API** [C]. It was built for this use case. It exposes availability, a five-minute slot lock, create, lookup by phone, modify and cancel. Bookings land in OpenTable for Restaurants as "phone/in-house" reservations.

There is no self-serve key. Access requires a partner application, a signed agreement, a sandbox build, a quality assurance certification of at least 14 days in which OpenTable's testers phone your agent, and an Integrations Marketplace onboarding tile [C].

Every shortcut is either prohibited or does not exist. The July 2026 Client Agreement bans credential sharing and automated access to the restaurant's account and lets OpenTable terminate the restaurant immediately for a breach [C]. The consumer Terms of Use ban bots and AI agents [C]. There is no official OpenTable app on Zapier, Make or n8n [C].

**Verdict: Go, with narrow conditions.** Build the capture loop now with a human-in-the-loop booking step, apply for partnership on day one, and do not expect sanctioned direct writes for three to nine months. Do not build a generic "AI that books straight into OpenTable" product. More than 20 certified partners already do that, including Yelp Host at $249 per month.

---

## 2. What it takes: requirements for sanctioned direct write access

All items below are [C] from docs.opentable.com and the api-partners pages unless marked.

| # | Requirement | Detail |
|---|---|---|
| 1 | Partner application | Apply at opentable.com/restaurant-solutions/api-partners/become-a-partner. Five steps: contact details, email and phone verification, company details including registration date and whether the product is live, product details. |
| 2 | What the form asks | Whether you want to let users make reservations, read data, or post data into table management. Monthly active users. Number of live restaurant locations. OpenTable restaurants already using your product. Other table management systems you integrate with. |
| 3 | Review and contract | "Access to our APIs is subject to approval and requires the execution of a formal agreement." Eligibility depends on "the nature of the partnership, use case, and technical feasibility." Third parties cite 3 to 4 weeks to first contact [V]. |
| 4 | Pricing | Unpublished. "Communicated during the approval and contracting process." OpenTable reserves the right to charge for the developer portal. |
| 5 | Authentication | OAuth 2.0 client credentials. `Authorization: Basic base64(client_id:client_secret)` to `{oauth}/api/v2/oauth/token?grant_type=client_credentials`. Hosts: `oauth-pp.opentable.com` (pre-production) and `oauth.opentable.com` (production). Bearer token after that. |
| 6 | Transport and idempotency | HTTPS with TLS 1.3 only since Oct 6, 2025. Every POST, PUT and PATCH should carry a unique `X-Request-Id` so retries are idempotent. |
| 7 | Sandbox | Approved partners only. Voice AI test restaurant IDs: 264001, 1040230 (card hold, deposit and experience scenarios), 268549, 138712. |
| 8 | QA certification | "A minimum window of 14 days" to review the pre-production build. OpenTable testers call a phone number you provide against RID 1040230. Scenarios cover availability, no-availability response, experiences, create, modify, cancel including RedirectToHost, lookup with several reservations, and correct attribution to your partner ID. "We require product certification and full onboarding flow for go-live." |
| 9 | Integrations Marketplace tile | You must build a restaurant onboarding and offboarding flow, OAuth preferred or a unique-identifier flow, with SVG logos, value proposition copy and up to six onboarding steps. Restaurants switch you on under OpenTable for Restaurants → Integrations → Phone automation. |
| 10 | Restaurant plan tier | Voice AI integrations are "available to restaurants subscribed to OpenTable Core and Pro in supported regions." Restaurants pay OpenTable nothing extra; the voice vendor sets its own price. |
| 11 | Rate limits | Not published. "Please contact your OpenTable representative." |
| 12 | Support | api@opentable.com, 3 to 5 business days. |
| 13 | Ongoing terms | API Platform Policy: no credential sharing, no use on behalf of third parties unless permitted, no scraping, suspension "for any or no reason," no obligation to provide support. |

**Realistic timeline [I]:** application review (weeks), contract negotiation, sandbox build (two to four weeks of work), certification (14 days minimum plus fixes), Marketplace tile. Three to nine months end to end.

**What the scale questions imply [I]:** the form asks for monthly active users, live locations and OpenTable restaurants already using you. A pre-revenue solo applicant with zero locations answers all three with zero or near zero. No minimum is published [U], and no first-hand acceptance or rejection stories were found on Reddit, Hacker News or Stack Overflow [U]. The safest reading is that OpenTable wants evidence of a live product and real restaurant demand. Pilot restaurants and support letters are the lever you control.

**Can a single restaurant get its own credentials?** The partner FAQ says "restaurants and their third parties can look to consume our APIs directly. If you are a restaurant, please work with your account management team" [C]. The only documented restaurant-side access is the read-only Sync API, granted through an account manager and a DocuSign naming the vendor (Klaviyo's setup is the example) [C]. No evidence was found of a single restaurant receiving Voice AI booking credentials [U]. Do not plan on it.

---

## 3. How captured data becomes a reservation

### 3.1 The API flow [C]

1. **Availability.** `GET /inhouse/v1/availability/{rid}?party_size&start_date_time&forward_minutes&backward_minutes`. Search window up to ±180 minutes. No availability returns HTTP 200 with empty arrays. Availability metadata at `GET /v2/availability-metadata/{rid}`.
2. **Lock the slot.** `POST /inhouse/v1/booking/{rid}/locks`. Holds the slot for exactly five minutes, "hard coded and cannot be edited." Party size 20 or fewer. Returns a `reservation_token`. Table types: default, highTop, outdoor, bar, counter.
3. **Create.** `POST /inhouse/v1/booking/{rid}/reservations` with the token. Lands as a phone reservation in OpenTable for Restaurants, source "phone/in-house."
4. **Lookup.** `POST /inhouse/v1/booking/{rid}/reservations/search` by phone number and date. Returns future active reservations, at most 10 (random if more). "Partners are responsible for accurately identifying the specific reservation."
5. **Modify.** `PUT /inhouse/v1/booking/{rid}/reservations/{id}`. Standard reservations only.
6. **Cancel.** `DELETE /inhouse/v1/booking/{rid}/reservations/{id}`. Cancelling a card-hold or deposit booking outside its policy window returns `403 RedirectToHost`, which means a human must handle it.
7. **Policies.** `GET /v2/booking-policies/...` and `GET /v2/cancellation-policies/...`. The agent must state deposit or card-hold amounts before booking.

### 3.2 Mapping what the voice agent captures to what the API needs

| You capture today | API field | Required? | Gap to close |
|---|---|---|---|
| Name (one field) | `first_name`, `last_name` | **Both required** | Agent must collect both names separately. |
| Phone number | `phone {number, country_code}` | **Required, SMS-capable mobile only** | Landlines are not supported. Validate with libphonenumber. Confirm "is this a mobile?" |
| Time | `start_date_time` via lock | **Required** | Must be on a 15-minute boundary, at least 15 minutes ahead, within 730 days. The API treats 5 AM as the start of a business day, so a 1 AM request belongs to the previous night's service. |
| Party size | `party_size` | **Required**, 1 to 20 | Over 20 goes to the restaurant. Vendors cap online at 6 to 8 and route larger to staff. |
| Notes | `special_request` | Optional | Maps cleanly. |
| (not captured) | `sms_notifications_opt_in` | **Required** | Ask verbally: "Can we text your confirmation to this number?" Log the consent sentence. Without opt-in, card-hold links do not go out. |
| (not captured) | `restaurant_id` (RID) | **Required** | Per-location config. |
| (not captured) | `dining_area_id`, `table_type` | Optional but a trap | More than 90% of restaurants use dining areas. If every area is assigned and you omit them, availability returns `NoAvailability`. |
| (not captured) | `X-Request-Id` | Should send | Your idempotency key. |

Other limits to design around [C]: no ticketed experiences; experiences cannot be modified or cancelled by API; OpenTable's 2% service fee cannot be passed to guests; restaurants can split inventory into Online, In-House and Walk-In, and the API only sees what the restaurant has opened to it ("why is the API not returning availability when it is visible online?" is an FAQ).

### 3.3 Why "Airtable row, then book later" fits the API poorly

The In-House API is a live conversation protocol, not a batch import. The lock lasts five minutes. No-availability is a 200 with empty arrays, which is a prompt to offer alternatives while the guest is still on the line. The certification tests exactly that: alternatives, deposit disclosure, RedirectToHost handling. A row booked an hour after the call cannot offer alternatives, cannot read a deposit policy to the guest, and leaves every failure for staff to untangle. The user's "capture loop" idea is right for the data path and wrong as the booking moment [I].

**Recommendation: two phases, one codebase.**

- **Phase 1, build now: async capture loop with a manual adapter.** End-of-call report → FastAPI → Airtable row → worker validates and normalizes → staff notified with a fully formatted request → staff key it into OpenTable for Restaurants in under a minute → status flips in Airtable → guest gets a text. This works today, needs no OpenTable permission, and reuses most of Yapper AI.
- **Phase 2, once partner access exists: mid-call tool calls.** Vapi custom tools `check_availability` and `create_reservation` hit the same FastAPI service, which calls the same normalizer and a real `OpenTableAdapter`. The guest hears the confirmation number before hanging up. The end-of-call report still writes the system-of-record row and triggers the SMS.

### 3.4 Data schema essentials

| Field | Why |
|---|---|
| `idempotency_key` = sha256(vapi call id + version) | Never ingest or book twice |
| `guest_first_name`, `guest_last_name` | Both required by API |
| `guest_phone_e164`, `sms_consent` | Mobile only; consent logged |
| `party_size` | 1 to 20 |
| `requested_date_raw`, `requested_time_raw` | Verbatim phrases, server resolves them |
| `requested_start_local`, `requested_start_utc`, `timezone` | Normalized, slot-rounded, IANA zone |
| `location_id` → Locations table (RID, hours, slot size, max party, adapter) | Per-restaurant config |
| `special_requests`, `occasion`, `seating_preference`, `accessibility_needs` | Surface to staff |
| `status` enum, `retry_count`, `next_attempt_at`, `last_error` | State machine and dead letter |
| `external_reservation_id`, `adapter`, `approved_by` | Confirmation and audit |
| `source_call_id`, `recording_url`, `transcript`, `captured_at` | Traceability |

Status flow: `new → validated → (pending_approval →) approved → booking → booked → confirmed_sent`, with side states `invalid`, `no_availability`, `duplicate`, `needs_review`, `cancelled`, `failed_permanent`. Only FastAPI writes `status`; humans only move `pending_approval → approved` and `needs_review → approved | cancelled`.

The voice agent emits raw phrases ("this Friday", "around 7") and the server resolves them with `dateparser` plus `zoneinfo`. Do not let the model compute dates. Validate against opening hours, the 15-minute grid, lead time and party limits. Dedupe on phone plus location plus a three-hour window.

### 3.5 The adapter pattern

```python
class BookingAdapter(Protocol):
    name: str
    async def check_availability(self, loc, start, party, window_min=90) -> Availability: ...
    async def create_reservation(self, req, slot, idempotency_key) -> BookingResult: ...
    async def find_reservation(self, loc, phone_e164, start) -> BookingResult | None: ...
    async def cancel(self, loc, external_id, reason) -> BookingResult: ...

# adapters: ManualAdapter (day one), FakeAdapter (tests), OpenTableAdapter (after approval)
```

`ManualAdapter` returns `pending_manual`, notifies staff, and waits for a confirmation number to be typed into Airtable. `OpenTableAdapter` does lock → create with `X-Request-Id`. Both sit behind the same interface, so phase 2 is a tool definition and one endpoint, not a rewrite.

### 3.6 Idempotency, three layers

1. **Ingest.** Postgres `UNIQUE(idempotency_key)` on a small Railway Postgres (about $5). Vapi or a proxy may redeliver the end-of-call report. Airtable has no compare-and-swap, so Postgres is the lock.
2. **Booking attempt.** `UNIQUE(request_id)` with an `in_flight` claim via `UPDATE ... WHERE state='pending' RETURNING`.
3. **Platform.** Send `X-Request-Id`. A timeout after a POST is ambiguous, not failed, so before any retry call `find_reservation(phone, start)` and adopt an existing booking rather than booking again.

Retries with `tenacity`: 30s, 2m, 8m, 30m, 2h, then `needs_review`. Retry only on 5xx, 429 and network errors. 4xx goes straight to review.

### 3.7 The Yapper AI lesson, carried forward

The 84-empty-rows bug came from webhooks firing on mid-call events before the structured output existed. Keep the fix: the `/vapi/events` endpoint ignores every event type except `end-of-call-report`, validates against a locked Pydantic schema with `extra="forbid"`, and skips when intent is not `new_reservation` or structured output is null. Read structured output from `artifact.structuredOutputs` (newer) or `analysis.structuredData` (older) and log one real payload before finalizing the parser; forum users report the schema is not always respected, so validate server-side regardless [C, Vapi docs and support threads]. Keep the regression test that posts `status-update`, `transcript`, `conversation-update` and `tool-calls` and asserts zero rows.

For phase 2 Vapi tools: return HTTP 200 with `{"results":[{"toolCallId": "...", "result": "<flat string>"}]}`; non-200 means the agent hears "no result." Target p95 under three seconds, hard-cancel the adapter at four seconds inside FastAPI, and configure `request-failed` to say "I've noted your request, the restaurant will text to confirm," never "you're booked." A circuit breaker drops the tool into capture-only mode when the backend is failing.

---

## 4. The routes, compared

| Route | Who authorizes it | Effort | Time to ship | Risk | Fit |
|---|---|---|---|---|---|
| **A. Official Voice AI API partnership** | OpenTable, via application, contract, certification | High: adapter, tile, OAuth onboarding, certification scenarios | 3 to 9 months, acceptance uncertain for a solo pre-revenue applicant | Low once approved; suspension "for any or no reason" per policy | The end goal. Only route that gives a true "booked while on the phone" result. |
| **B. Human-in-the-loop** (capture → formatted SMS/Slack to host → host keys it into OpenTable for Restaurants → status button → guest text) | Restaurant alone. Staff-entered bookings are ordinary phone/in-house reservations, free of network cover fees [C, Client Agreement "Cover Fee"] | Low to medium, ~45 to 65 hours | 2 to 6 weeks plus 10DLC wait | Low legal risk. Operational risk: host forgets, guest told "request received" not "booked" | Phase 1. Compliant today. Weak against "does it book straight into OpenTable?" |
| **C. SMS deep link to the guest** (`opentable.com/restref/client/?rid=X&restref=X&datetime=YYYY-MM-DDTHH:MM&covers=N`) | Guest books themselves. Pattern is widely used in code but undocumented; parameter casing varies, test per restaurant [C in code / U officially] | Low | Days | Counts as an online booking. May carry per-cover fees (website-widget covers reported at $0.25 on Basic, free on Core; network covers $1 to $1.50) [V]. Lower completion; Popmenu reports links sent on 25% of calls, no completion data [V] | Cheap fallback. Popmenu and NextPhone sell exactly this. |
| **D. Resell, white-label or integrate with a certified partner** (Slang, Hostie, Maple, Loman, PolyAI, VoicePlug, Yelp Host and others) | The partner. No published reseller programs found; Slang has only a referral ambassador program [U/V] | Low build, high sales | Weeks if a partner agrees | Margin and dependence | Lowest-risk way to say "yes, it books into OpenTable" this quarter. |
| **E. Target open platforms or no platform** (resOS: restaurant-issued keys; Formitable: restaurant-granted permissions; Eat App, Quandoo, ResDiary £150/month, TheFork, Zenchef: keys on request; or your own book in Postgres/Airtable for restaurants without a system) | Restaurant and the platform | Medium: one adapter per platform | Weeks | Small US footprint for the EU platforms; your own book means you become the reservation system | Good niche for independents off OpenTable. Switching OpenTable restaurants is impractical: early exit costs 100% of remaining fees in the initial term [C]. |
| **F. RPA / browser automation on the restaurant's login** | Nobody. **Prohibited.** | Medium plus endless maintenance; 2FA, SSO, Akamai bot protection | n/a | Restaurant loses its whole reservation system | **Do not build.** See quotes below. |
| **G. Bot on the consumer site or app** | Nobody. **Prohibited.** | Medium, fragile | n/a | Terms of Use §13 bans "robot, spider, scraper, generative AI or other AI technology... automated assistants"; §18.2 makes the user liable for its AI agent; network cover fees; wrong identity on the booking | **Do not build.** |

**Why F is closed even with the restaurant's consent.** From the OpenTable Client Agreement (Americas), updated 2026-07-22 [C]:

- §2.2(a): "Each User must keep its login credentials confidential and not share them with anyone else."
- §2.2(b): any service provider or third party accessing the Services "must enter into a separate agreement with OpenTable prior to Client granting access."
- §2.3(j): Client will not "use any automatic or manual device, process or means to access, search, copy or monitor any portion of the Services (except as expressly authorized by OpenTable)."
- §14.5: OpenTable may suspend or terminate "immediately if Client breaches Section 2.3 (Restrictions)."

Consent does not authorize the access. It moves the breach onto the restaurant, which then faces immediate termination plus the early-exit penalty. OpenTable's own security guidance says a vendor asking for credentials "is a red flag" [C]. *Facebook v. Power Ventures* adds CFAA exposure for the vendor once OpenTable sends a notice [C]. The SevenRooms precedent, where OpenTable blocked login-based data sharing until a paid integration was signed, shows OpenTable enforces this [C].

**Other non-routes checked:** Reserve with Google syncs into OpenTable but exposes no booking API to third parties; partners must be booking platforms and integration takes 12 to 16 weeks with two engineers [C]. The POS integration exchanges check data, not reservations [C]. No email or ICS ingestion exists [U]. Make lists a community OpenTable app of unknown capability [U]. Unified.to lists "create reservation" for OpenTable but almost certainly still requires your own partner approval [I].

---

## 5. Practicality assessment

### 5.1 Market facts

| Fact | Figure | Label |
|---|---|---|
| OpenTable network | About 65,000 restaurants worldwide; Booking Holdings owned | [C] |
| OpenTable voice AI program | More than 20 voice AI partners; 3M diners seated via voice AI, up 270% year over year (Aug 26, 2026 release) | [C] |
| Named partners on OpenTable's page | Axify, Bonnie, Certus, Hey Truffle, Hostie AI, Loman, Maitly, Maple, Millie AI, PolyAI, Sadie, Slang AI, Tablevoice, TimeShark, Timmy AI, VoicePlug, Yelp Host | [C] |
| Native OpenTable phone agent | None. OpenTable's AI is the diner-facing Concierge (500k+ MAU) plus LLM platform links | [C] |
| Yelp Host | Books directly into OpenTable since July 28, 2026 (US and Canada), $249/month or $199 for Guest Manager users | [C] |
| Vendor pricing per location per month | Maple $85 to $150 (Pro $220 to $350); Hostie from $199; Loman $199 to $529; Popmenu $299 to $528 (texts a link); Slang $399 to $599 | [V] |
| Call mix (Maple, 1.2M calls) | 38% reservations, 22% hours and location, 15% menu, 12% takeout, 7% events | [V] |
| Conversion (Maple) | 64% of reservation calls end in a completed reservation; average party 3.2; about $134 value per reservation call | [V] |
| Missed calls | Full-service about 9% (REVMO, 12k calls); up to about 33% at peak (Maple); PolyAI claims 30 to 60% for groups | [V] |
| Value of a recovered booking | About $70 to $85 casual, $170 to $360 fine dining, assuming party of 2.5 to 3 | [I] |
| Phone share of reservations today | Unknown. The "71.7% by phone" figure is from a 2011 Cornell study | [U] |

### 5.2 Competitive squeeze

The exact product the user described already exists from more than 20 certified vendors, with a price floor near $85 and a well-distributed incumbent (Yelp Host) at $249 that books into OpenTable. Slang markets directly against "link-sending" competitors. Core and Pro restaurants, the only ones who can enable voice integrations, already have 17 tiles to choose from. Basic-tier restaurants cannot enable any voice partner, which makes them the one unserved OpenTable segment, and also the most price-sensitive. OpenTable's April 2026 "System of Record" mandate and its public framing of scrapers as "bad actors" point to tighter, not looser, policing of unofficial integrations [C].

### 5.3 Legal and compliance

- **Wiretap (CIPA).** *Taylor v. ConverseNow* (N.D. Cal., Aug 11, 2025) let California wiretap claims proceed against a restaurant AI phone vendor, with the deploying restaurant facing aiding-and-abetting exposure, partly because call data was used to improve models [C]. Mitigation: upfront "AI assistant, this call may be recorded" disclosure, no training on customer calls without consent, data-processing agreement with each restaurant.
- **Recording consent.** All-party consent in roughly a dozen states (CA, FL, IL, MD, MA, MT, NH, PA, WA among them). Disclose everywhere rather than branching by state [V].
- **SMS.** Transactional confirmations to a number the guest gave are generally covered by prior express consent; still capture `sms_consent` verbally. No marketing texts without written consent. Honor STOP within 10 business days (FCC, April 2025). A2P 10DLC registration is mandatory and takes 3+ weeks; toll-free verification is an alternative [C].
- **AI disclosure.** Utah SB 226 (May 2025) requires disclosure when asked, with a safe harbor for upfront disclosure [C]. The FCC's Feb 2024 ruling classes AI voices as "artificial" under TCPA, mainly affecting outbound calls [C]. Colorado's AI Act was replaced by SB 26-189 (effective 2027) focused on consequential decisions, not reservations [C].
- **PCI.** Never take card numbers by voice. OpenTable collects card holds by SMS link itself; for your own flows use a hosted payment link.
- **PII.** Purge transcripts and recording URLs after 30 to 90 days; restrict Airtable sharing; treat allergy and accessibility notes as sensitive.

### 5.4 Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | Partner access denied or slow | Medium to high | High | Apply day one with pilot restaurants' support; ship phase 1 regardless |
| 2 | ToS breach terminates the restaurant's account (§2.2, §2.3(j), §14.5) | High if automating logins | Severe | Never use credential-based automation; only the official API or a human |
| 3 | Double bookings | Medium without a live inventory read | High | Three-layer idempotency; "request received" language until a confirmation number exists |
| 4 | Misheard date, time or party size | Medium | Medium to high | Read-back with weekday, raw phrases resolved server-side, SMS summary, ambiguity flags force review |
| 5 | SMS, TCPA or 10DLC failure | Medium | Medium | Register early, transactional only, honor STOP |
| 6 | Wiretap or recording claims | Medium in all-party states | High | Upfront disclosure, no model training on calls, DPA with restaurant |
| 7 | Incumbents commoditize the niche; OpenTable ships a native agent | High, already happening | High | Specialize: Basic-tier and off-platform independents, private dining and events intake, multilingual, hands-on local setup |
| 8 | Restaurant churn and liability for wrong bookings | Medium to high | Medium | Month-to-month pricing, "request not guarantee" clause, liability cap, E&O insurance |

### 5.5 Verdict

**Go with conditions, and keep the scope narrow.** The technical side is tractable and most of it is already built in Yapper AI. The hard part is permission. A sanctioned direct write into OpenTable is a months-long partnership process with an uncertain outcome for a pre-revenue applicant, and the only alternatives are prohibited or do not exist. What is practical today is a compliant capture loop with human confirmation, a texted booking link as a fallback, and a partner application running in parallel. What is not practical is competing head-on with 20+ approved vendors on "books straight into OpenTable." The defensible positions are the segments they do not serve: Basic-tier and off-platform independents, event and private-dining intake, and restaurants on platforms that issue their own API keys.

---

## 6. Recommended plan

**Day 1**
- Submit the OpenTable partner application at opentable.com/restaurant-solutions/api-partners/become-a-partner. Select "let users make reservations" and "post data into table management." Be honest about scale; attach pilot restaurant names and letters if you have them. Email partnersupport@opentable.com with a one-paragraph use case.
- Start Twilio A2P 10DLC (or toll-free verification). Budget three weeks.
- Decide on the first two or three pilot restaurants. Prefer one on OpenTable Core or Pro (future API customer) and one or two with no reservation system (your own book, full automation now).

**Phase 1: async capture loop with manual adapter (weeks 1 to 4, about 45 to 65 hours)**

| Component | Hours | Reuse from Yapper AI |
|---|---|---|
| Vapi assistant: both names, mobile check, party size, raw date and time phrases, read-back, SMS consent line, AI and recording disclosure | 4 to 6 | High |
| FastAPI `/vapi/events`: end-of-call-report only, Pydantic `extra="forbid"`, Postgres idempotency | 4 to 6 | High |
| Airtable base: Requests, Locations, Closures, Events; Interface with status kanban and Needs-review view | 3 to 5 | Medium |
| Normalization: dates, times, 15-minute grid, hours, phone, names, dedupe, plus tests | 10 to 14 | Low to medium |
| Adapter interface, ManualAdapter, FakeAdapter | 4 to 6 | New |
| Worker state machine, retries, dead letter | 6 to 8 | Medium |
| Twilio SMS out and inbound reply handling | 5 to 8 | Medium |
| n8n: stuck-row sweeper, restaurant notify, daily digest; Airtable automation for approval and mark-booked | 3 to 5 | High |
| Fifteen test-call scenarios and fixes | 5 to 8 | Medium |

**Phase 1 gate:** ten real calls in a row produce one complete row each, zero duplicates, staff confirm within 30 minutes, and the guest receives a correct text.

**Phase 2a: own-book real-time booking (weeks 4 to 8, 12 to 18 hours)**
- Add Vapi tools `check_availability` and `create_reservation` against a Postgres book for restaurants without a platform (the n8n template #19500 pattern). This proves the mid-call architecture and gives you a demo that books live.

**Phase 2b: OpenTable adapter (only after approval, 10 to 20 hours plus certification)**
- Implement `OpenTableAdapter` against the pre-production host and test RIDs. Script the certification scenarios: no availability, alternatives, deposit disclosure, RedirectToHost, multi-reservation lookup, partner attribution. Build the Marketplace tile with OAuth onboarding. Submit and allow 14+ days.

**Fallbacks to carry throughout**
- SMS deep link to the restaurant's OpenTable page for guests who prefer self-service; test the `restref` parameters per restaurant.
- A conversation with one or two certified partners (Maple, Hostie, Loman) about referral or white-label terms, so you can say "yes" to OpenTable today if a prospect insists.

**What to tell prospects**
- Today: "Every call is answered, the request is captured and texted to your host stand in a tap-to-confirm format, and the guest gets a confirmation text. Phone bookings your staff enter are free of OpenTable cover fees."
- Do not promise: "It books straight into OpenTable." Say: "Direct OpenTable integration is in OpenTable's partner review; we will enable it for you when certified."

**Go/no-go gates**
1. Phase 1 gate above fails after two iterations: stop and fix data quality before anything else.
2. No partner contact within eight weeks of applying: lean into own-book and open-platform restaurants, and pursue the white-label conversation.
3. Partner application rejected: the product is "capture plus confirm plus link," priced near Maple's floor, sold on service and specialization, or it is a referral business for a certified partner.
4. Any prospect asks you to use their OpenTable login: decline, every time.

---

## 7. Conflicts between the reports and open questions

| Topic | Report A says | Report B says | Resolution |
|---|---|---|---|
| OpenTable plan prices | Basic $149, Core $299, Pro $499 per month, plus $1 per network cover on Core and Pro (search snippets of OpenTable plan pages) | Basic $39, Core $249, Pro $449 (Capterra, 2026); other blogs differ again | Trust OpenTable's own plan pages over aggregators, but prices vary by region and change often. Confirm with an account team. Either way, voice integrations need Core or Pro. |
| Yelp Host price | $249 per month, $199 for Guest Manager users (Yelp blog, July 2026) | $149 per month, $99 for Guest Manager users (launch coverage, Oct 2025) | Likely a price increase between launch and the OpenTable integration. Use the July 2026 figure. |
| Plan needed for voice integrations | "OpenTable Core and Pro" (OpenTable support article) | "Premium or Hospitality Plus" (Hostie knowledge base) | OpenTable's naming wins. Hostie's article probably uses older tier names. |
| Can a single restaurant get Voice AI credentials? | FAQ: restaurants "can look to consume our APIs directly" via their account team | No evidence of booking credentials for a restaurant; only Sync API data export documented | Unknown. Ask the restaurant's account manager directly. Plan as if the answer is no. |
| Voice AI API endpoint shape | Both docs-based reports agree on paths, lock duration and required fields | Hostie and ainora blogs give similar but not identical details | Trust docs.opentable.com. |
| Missed-call rates | 9% full-service (REVMO) | 33% at peak (Maple), 36% or 65% (Hostie, self-contradicting) | Use REVMO for the base case and Maple for the peak case. Discount Hostie. |
| MJ AI Systems "reads live seating from the OpenTable API" (Vapi plus Make agency) | Unverified | Unverified | Treat as unverified. Could be a partner, an own-book demo, or marketing. |
| Unified.to lists "create reservation" for OpenTable | Unverified | Unverified | Assume it still requires your own OpenTable partner approval. |
| Rate limits | Not published (docs) | "Typical" limits listed by Hostie without a source | Not published. Ask your representative. |

**Questions to put to OpenTable directly**
1. Does a pre-revenue vendor with two to three pilot restaurants qualify for the Voice AI API, and what are the actual fees?
2. Can a single Core or Pro restaurant obtain in-house booking credentials for its own vendor, or must the vendor be a certified partner?
3. Which plan tiers in the US can enable Phone automation tiles today?
4. Do `restref` website-referral bookings incur a cover fee on each tier, and what is the current fee schedule?
5. Does the API see in-house inventory by default, or must the restaurant open it per partner?
6. What are the rate limits and the SLA for the pre-production environment?

**Things to verify yourself before building on them**
- The exact structured-output location in your Vapi end-of-call payload (`artifact.structuredOutputs` vs `analysis.structuredData`).
- Whether `server.timeoutSeconds` applies to Vapi function tools on your account.
- The `restref` link parameters against one live restaurant.
- Twilio toll-free verification timelines.
- The all-party-consent state list and TCPA guidance with a lawyer; nothing here is legal advice.

---

## 8. Sources

**OpenTable primary sources [C]**
- docs.opentable.com (Postman collection, includes In-House Booking API aka Voice AI API, Online Booking API, Sync, CRM, POS, API Platform Policy): https://docs.opentable.com/ and raw collection JSON https://docs.opentable.com/api/collections/38767429/2sAXxTcWRy?segregateAuth=true&versionTag=latest
- API partners landing: https://www.opentable.com/restaurant-solutions/api-partners/
- Become a partner application: https://www.opentable.com/restaurant-solutions/api-partners/become-a-partner/
- API partner FAQs: https://www.opentable.com/restaurant-solutions/api-partners/faqs/
- Developer portal terms (July 22, 2026): https://www.opentable.com/restaurant-solutions/api-partners/terms-and-conditions/
- Voice AI partner page: https://www.opentable.com/restaurant-solutions/products/reservation-management/voice-ai/
- Client Agreement, Americas (updated 2026-07-22): https://opentable.my.salesforce-sites.com/restaurantterms/resource/1599787212000/restaurant_client_agreement_americas
- Consumer Terms of Use (revised 2026-07-22): https://www.opentable.com/c/legal/terms-and-conditions/
- Security and integrations guidance (Oct 3, 2025): https://www.opentable.com/restaurant-solutions/resources/security-and-integrations-on-opentable-what-you-should-know/
- Using voice AI with OpenTable (support): https://support.opentable.com/s/article/Using-voice-AI-with-OpenTable?language=en_US
- Aug 26, 2026 product release (20+ voice partners, 3M diners, 270%): https://www.prnewswire.com/news-releases/opentable-launches-its-largest-suite-of-new-and-updated-product-features-for-restaurants-302860569.html
- Integrations page: https://www.opentable.com/restaurant-solutions/integrations/
- Connect product page (now Basic/Core/Pro): https://restaurant.opentable.com/products/connect/

**Voice vendors and partners**
- Yelp Host adds OpenTable (July 28, 2026) [C]: https://blog.yelp.com/news/yelp-host-voice-ai-adds-opentable-reservations-and-takeout-ordering-for-restaurants/
- Yelp Host launch (Oct 2025) [C]: https://www.businesswire.com/news/home/20251021484748/en
- Slang and OpenTable [C]: https://www.slang.ai/press-releases/slang-partners-with-opentable
- PolyAI and OpenTable [C]: https://poly.ai/our-partners/opentable
- Loman and OpenTable [C]: https://loman.ai/integrations/opentable
- Maple and OpenTable [V]: https://maple.inc/integrations/opentable.md
- Maple call study, 1.2M calls [V]: https://www.maple.inc/blog/the-state-of-restaurant-phone-communication-insights-from-1-million-calls
- VOICEplug and OpenTable [C]: https://www.prnewswire.com/news-releases/voiceplug-ai-and-opentable-announce-global-integration-to-automate-table-reservations-302624266.html
- Hostie OpenTable setup (plan naming conflict) [V]: https://knowledge.hostie.ai/how-to-set-up-an-opentable-integration
- DM Champ OpenTable onboarding example [C]: https://help.dmchamp.com/integrations/opentable/
- Popmenu Answering (link handoff) [V]: https://get.popmenu.com/answering
- NextPhone (link handoff) [C]: https://www.getnextphone.com/integrations/opentable
- SevenRooms Voice AI [V]: https://sevenrooms.com/platform/VoiceAI/ and https://elevenlabs.io/blog/sevenrooms
- REVMO 2026 call report [V]: https://wp.revmo.ai/wp-content/uploads/2026/04/REVMO_STATE-OF-CALLS-REPORT-2026-SS.pdf
- Vendor pricing [V]: https://pricingsaas.com/companies/slangai, https://loman.ai/blog/maple-reviews-pricing-alternatives, https://www.cloudtalk.io/blog/loman-ai-pricing/

**Alternative platforms**
- Third-party audit of restaurant booking APIs (Sept 5, 2026) [V]: https://ainora.lt/blog/restaurant-booking-api-for-ai-agents-2026
- resOS API [C]: https://resos.com/api
- Formitable API [C]: https://help.formitable.com/hc/en-us/articles/18305483571613-How-to-integrate-with-a-restaurant-via-the-Formitable-REST-API
- Yelp Reservations API (partner-only) [C]: https://docs.developer.yelp.com/docs/reservation
- ResDiary API [C]: https://help-resdiary.theaccessgroup.com/en/articles/16108724-explore-and-request-your-resdiary-api
- Eat App partner API [V]: https://restaurant.eatapp.co/knowledge/using-the-eat-app-partner-api-to-get-and-post-availability
- Toast: no reservation API [C]: https://doc.toasttab.com/doc/cookbook/apiIntegrationChecklistReservation.html
- Reserve with Google integration overview [C]: https://developers.google.com/actions-center/verticals/dining/guides/end-to-end-integration/overview
- OpenTable pricing via aggregators [V]: https://www.capterra.ie/software/17313/opentable-for-restaurants and https://restaurant.eatapp.co/blog/opentable-pricing
- OpenTable blocks login-based data sharing (SevenRooms precedent) [C]: https://www.restaurantdive.com/news/opentable-blocks-data-sharing-with-competitors/550662/
- System of Record mandate coverage [C]: https://www.restaurantdive.com/news/open-table-client-agreement-updates-primary-table-mangement/815706/

**Deep-link pattern (undocumented, from code)**
- https://github.com/omarshahine/restaurant-cli (OpenTable provider), https://tessl.io/registry/skills/github/gooseworks-ai/goose-skills/restaurant-booking, https://skills.cat/skills/evansking/openclaw-shared/opentable

**Build stack docs [C]**
- Vapi custom tools: https://docs.vapi.ai/tools/custom-tools
- Vapi server events (end-of-call-report): https://docs.vapi.ai/server-url/events
- Vapi structured outputs: https://docs.vapi.ai/assistants/structured-outputs
- Vapi tool reliability and timeouts: https://docs.vapi.ai/tools/api-request/reliability
- Vapi structured data support thread: https://support.vapi.ai/t/28666139/structured-data-sometimes-not-sent-in-end-of-call-report
- Retell custom functions: https://docs.retellai.com/build/single-multi-prompt/custom-function.md
- n8n Airtable Trigger (polling): https://docs.n8n.io/integrations/builtin/trigger-nodes/n8n-nodes-base.airtabletrigger/
- Airtable webhooks: https://airtable.com/developers/web/api/webhooks-overview
- n8n restaurant reservation template #19500: https://n8n.io/workflows/19500-handle-restaurant-reservations-and-orders-with-elevenlabs-sheets-and-gmail/
- Twilio A2P 10DLC: https://www.twilio.com/docs/messaging/compliance/a2p-10dlc and https://support.twilio.com/hc/en-us/articles/14910496447771-Shutdown-of-Unregistered-10DLC-Messaging

**Legal**
- Taylor v. ConverseNow CIPA alert (Duane Morris) [C]: https://www.duanemorris.com/alerts/northern_district_california_allows_cipa_claims_against_ai_pizza_ordering_assistant_0825.html
- FCC AI voice ruling (Feb 2024) [C]: https://huntonak.com/privacy-and-information-security-law/fcc-issues-declaratory-ruling-that-tcpa-applies-to-ai-generated-voice-calls
- Utah SB 226 AI disclosure [C]: https://perkinscoie.com/insights/update/new-utah-ai-laws-change-disclosure-requirements-and-identity-protections-target
- Wiretap laws by state [V]: https://ktslaw.com/blog/globalprivacy-and-cybersecuritylaw/2024/7/wiretap-laws-in-the-united-states
- Facebook v. Power Ventures summary [C]: https://blog.apify.com/facebook-v-power-ventures/
- Colorado AI Act replacement [C]: https://www.mofo.com/resources/insights/260515-colorado-hits-reset-ai-regulation
- TCPA informational vs promotional texts [V]: https://www.compliancepoint.com/marketing-compliance/informational-vs-promotional-calls-and-texts-understanding-the-tcpa-rules/

*This report is research synthesis, not legal advice. Verify contract terms and compliance items with counsel before launch.*
