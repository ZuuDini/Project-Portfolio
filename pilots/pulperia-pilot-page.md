# AI Receptionist page, Pulpería pilot edition

Rewrite of every section of the `/ai-agents/appointment-setter` page so it describes the **free 30-day pilot at Pulpería Latin Mediterranean Kitchen** and nothing else. Everything that is not part of the pilot (calendar integration, a 1-week install, the generic ROI math, the "blueprint call") is dropped. A rendered mock-up of the result is in `pulperia-pilot-page.html`.

Sources (AI Hivemind, Oct 17–21 2026): `Shared/Free Client Reactivation Plan.md` (pilot terms), `Shared/Plans/Pulperia Victor Meeting Prep 2026-10-20.md` and the one-pager (what we say and don't say, the scorecard), the W3 10-20 and 10-21 daily logs (meeting outcome, the four before-go-live items), `docs/pilots/free-pilot-agreement-template.md` (agreement terms), `Shared/Plans/Restaurant AI Receptionist Competitive Pricing 2026-10-20.md` (why no price on the page).

Rules applied throughout:
- **No invented numbers.** The anti-fabrication rule in the pilot plan: a result comes from the scorecard, not from memory or an estimate. The old page's $16,200/month cost and $160,800/year value are generic and go.
- **Say only what is true today.** Nothing writes into OpenTable or Resy. The host alert and the missed-call sheet are pilot setup, not live yet, so the page calls them "before go-live", never "your team sees it right away".
- **Requests, not bookings.** After the demo, the agent must never offer, refuse or confirm a time. Every section says "reservation request".
- **No price up front.** The one-pager says price is set together at day 30. The page does the same.
- **No individual names or personal numbers.** Public page, public repo. People are referred to by role.

---

## 1. Hero

| | |
|---|---|
| **Was** | "Inbound AI Appointment Setter. Convert inbound calls into booked appointments automatically." |
| **Now** | Eyebrow: *Free 30-day founding pilot*. Title: **AI phone receptionist for Pulpería**. Sub: *Picks up the calls your team can't get to, in English and Spanish, 24/7. Only the calls you miss. Your number never changes.* Four facts under it: 30 days or 300 call minutes · $0, no card, no contract · Off in 10 seconds (`*73`) · Your call data is yours. |
| **Why** | Restaurants take tables, not appointments. "Books automatically" is exactly what the pilot does not do. The four facts are the pilot terms from the Reactivation Plan and the one-pager. |

## 2. The Problem

| | |
|---|---|
| **Was** | Generic bullets (voicemail, phone tag, double-bookings) and a "Cost Per Month" box totalling $16,200 from made-up volumes. |
| **Now** | Heading: **What a missed call costs Pulpería.** Bullets from the meeting and the public site: calls that ring out during service and after close · private events (up to about 100 guests) are booked by phone or email only, so an events call nobody picks up is a lost lead · requests taken by hand get forgotten or double-booked · Spanish-speaking callers · no record today of which calls were missed or what the caller wanted. The cost box becomes **Your numbers, filled in at week 0**: unanswered calls per week (from the carrier call log) · your average check per cover · what one lost Friday 8-top is worth. Line under it: *Day 30 is measured against your own baseline, not our estimate.* |
| **Why** | "How many calls we miss, that's real data" was the owner's own metric. The ops director's objection was nothing forgotten or booked twice. Events being phone/email only is on pulperianewyork.com/party. The baseline question is step one of the scorecard. |

## 3. The Solution

| | |
|---|---|
| **Was** | Five steps ending in "Book Appointment" (AI books it into your calendar) and "Automatic Follow-Up" (reminders 24 h before). |
| **Now** | Heading: **How the pilot receptionist works.** Six steps: **1 Only missed calls forward.** Busy or no answer (after hours too if you want), after 3–4 rings. Everything else stays with your host. **2 Sofia answers and says what she is.** "Pulpería, this is Sofia, the AI host. Calls may be recorded." English or Spanish, switching mid-call. **3 Answers the common questions.** Hours, location, menu and prices, brunch, pre-theater. Never promises a dish is allergen-free. **4 Takes a reservation request, not a booking.** Date, time, party size, name, phone, then email, plus occasion notes. She never offers, refuses or confirms a time: someone from the team gets back to you. Nothing goes into OpenTable or Resy; your host enters every booking. **5 The request reaches one supervisor.** Every finished call sends its request by text or email to the one person you name, within a minute of hang-up. The guest gets a text saying the request was received. **6 Anyone who asks for a person gets one.** Live transfer to the number you give us, or a callback message. No card numbers taken; complaints go straight to a manager. Footer line: *Every call adds a row to your missed-call sheet: time, caller number, what they wanted.* |
| **Why** | Steps 4–6 and the sheet are the four "before go-live" items in the 10-21 log (prompt fixes, supervisor alert, missed-call dashboard, forwarding). Calendar booking and 24-hour reminders are not in the pilot. |

## 4. Business Impact

| | |
|---|---|
| **Was** | "24/7 · 95% call-to-appointment conversion · −60% no-shows" and a Monthly Value table adding to $13,400/month, $160,800/year. |
| **Now** | Heading: **The 30-day scorecard, agreed before go-live.** Three tiles: **90%+** missed calls handled (share of AI-answered calls that end in a request, a message or an answered question; 90%+ go · 75–90% look closer · under 75% no) · **≤ 2** serious mistakes in 30 days (wrong hours or price, a request claimed with no text sent, a card number taken, a double booking) · **300** free minutes. Table **What you get each week**: calls caught · requests sent to your supervisor · requests that became bookings × covers × your average check (money recovered) · serious mistakes · your team's view from the 15-minute check-in. Line under it: *Week 0 sets the baseline. Day 30 is a decision against these numbers, then we set the price together. Numbers hit but something still open means go, with conditions.* |
| **Why** | The scorecard is from the meeting prep (Vapi playbook rule: set thresholds before data comes in). Percentages like 95% conversion have no source and would break the anti-fabrication rule. |

## 5. 1-Week Implementation

| | |
|---|---|
| **Was** | Day 1-2 Discovery, Day 3-4 Build (connect to calendar), Day 5-6 Test, Day 7 Launch. |
| **Now** | Heading: **From yes to day 30.** Four cards: **Day 0, agreement and intake.** One-page agreement: free, $0, no card, no auto-renew, either side can stop by email. The 8-item intake: carrier and forwarding login · hours · top 5 caller questions · reservation system · POS · supervisor phone or email for request alerts · transfer number · menu. About an hour of your time. **Before go-live, our setup.** Requests-only prompt with 3 test calls passing · supervisor alert wired and tested · missed-call sheet live · voice check · forwarding on your line, with an outside test call landing on the AI within 4 rings · you get the `*73` off switch. **Weeks 1–4, live.** Only missed calls. 15-minute check-in each week with the scorecard. Menu or hours change? Tell us, updated the same day. **Day 30, decide.** Results against the scorecard, together. A straight yes or no on a price we set together. If it worked: a short quote and introductions to two owners you know. If not: we turn it off and the data stays yours. Note under the cards: *Reservation-system integration (OpenTable, Resy) is not part of these 30 days. It only happens through their official APIs if those allow it, and it is a separate conversation after day 30.* |
| **Why** | The 10-21 log says the "a month, max" line about integration must be corrected at the first check-in, and OpenTable's platform policy bans automating the host UI. The go-live items are the log's four Pulpería rows plus the playbook's forwarding verification. |

## 6. What's Included

| | |
|---|---|
| **Was** | Six checkmarks including "Calendar integration (Google, Outlook, etc.)" and "SMS & email confirmation system". |
| **Now** | Three columns. **In the pilot:** AI host set up with Pulpería's hours, full menu and FAQ · English and Spanish · forwarding for busy and no-answer calls only · request text or email to your supervisor · "request received" text to the guest · live transfer or callback · missed-call sheet · weekly 15-minute check-in and scorecard · AI disclosure and recording notice on every call · `*73` off switch · 300 free minutes · your data stays yours. **Not in the pilot, on purpose:** writing into OpenTable, Resy or your POS · confirming availability · taking payments or card numbers · delivery orders · custom builds ("Possible later. Let's prove the phones first."). **What we ask in return:** a yes or no at day 30 · a short quote if the results are good · the 15-minute weekly check-in · intros to two owners if you're happy. |
| **Why** | The four asks are the agreed exchange in the Reactivation Plan and the agreement template. The "not included" column is the "never say yes to custom work" rule, stated as a strength. |

## 7. Call to action

| | |
|---|---|
| **Was** | "Ready to Never Miss Another Call? Book a 15-minute blueprint call. We'll analyze your current call volume, show you exactly how the AI would handle your calls, and calculate your specific ROI." Button: Book Your Blueprint Call. |
| **Now** | Heading: **Hear it answer as Pulpería.** Demo line (917) 722-4406, shown as text. *Ask for a table, the hours, or "can I talk to a manager?"* Then: *Next step: sign the one-page pilot agreement and pick a go-live date.* Button: **Confirm a go-live date**. No ROI calculator promise. |
| **Why** | The owner has already said yes verbally (10-20). The next action is the agreement and the intake, not a discovery call. "Calculate your specific ROI" would be an estimate, which the plan forbids. Check that the 917 number is still pointed at the Pulpería assistant before publishing. |

---

## Before this goes live on the site
- Confirm the 917 demo number still answers as Pulpería (the prep doc says to restore it once the owner decides).
- Confirm the supervisor alert and the missed-call sheet exist before the page says they do; until then they stay under "before go-live".
- Keep one brand on the page. The prep doc's rule for this prospect is **24-7 AI Phone Receptionist** only.
- The agreement is still an unsigned draft with blanks (provider address, client legal name and signer, contacts) and needs attorney review. The page says "one-page agreement" and nothing about its status.
