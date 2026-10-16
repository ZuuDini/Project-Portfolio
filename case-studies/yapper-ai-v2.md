# Yapper AI v2: 24/7 AI Receptionist (ZuuDini Labs)

**The problem:** Small trade businesses like plumbers, HVAC techs and electricians miss calls when they are on a job or after hours, and a missed call is often a lost job. I wanted to build an AI receptionist that answers every call, collects the caller's details and the job request, and logs everything so the owner can follow up.

**My role:** I was the only builder. I planned it, chose the tools, wrote the prompts, built the automations and kept a daily build journal. The repo has about 600 commits from me between October 2025 and March 2026. Near the end I used AI coding assistants to help write parts of the Python service, and I reviewed and tested what they produced.

**What I built:**
- Voice agent prompts for four industries: plumbing, HVAC, electrical and personal injury law. Each one has a prompt changelog.
- A call pipeline: the voice agent (first Bland, then Vapi) sends structured call data to Make.com and later n8n, which writes it to Airtable and notifies the owner by email.
- A FastAPI webhook service that checks incoming call data, logs it to Airtable, creates follow-up events in Google Calendar, and sends text and email summaries, with Railway deployment files and a 9-test webhook test suite.
- Operating documents: a setup guide, a troubleshooting guide, test call scenarios and edge cases, a 7-day client onboarding plan, and a beta program agreement.

**Constraints I worked through:** The hardest problem wasn't the AI. It was getting the data to arrive reliably. For about five weeks, call data kept reaching Make.com incomplete or empty. My first real test call created 84 empty records in Airtable. I wrote a root-cause analysis and found two causes. First, the webhook was firing during the call, before the agent had produced its final structured output. Second, every time I edited the prompt, the data format changed, and Make.com kept using the old format, so field mappings kept breaking. The fix was to lock down a stable assistant with a fixed data format, turn off the early events, and trigger only on the end-of-call report. After that, test calls produced complete structured data in n8n. I was also working with limited time and money, on a few hours a week alongside other commitments. So I tracked blockers by type (technical, mapping, strategy, fatigue) to stop myself from repeatedly rebuilding things that already worked.

**What changed:** I went from a prompt that did nothing to a working pipeline that captures a test call, structures it, logs it and notifies the owner. Along the way I wrote down the failures and their fixes. I don't have paying customers to report. What I took away is a habit I now use on every automation: fix the data format first, trigger only on final events, test with real calls early, and write down why something broke before rebuilding it.
