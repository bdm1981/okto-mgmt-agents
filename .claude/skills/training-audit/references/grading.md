# Grading

## Taxonomy

| grade | means | bar |
|---|---|---|
| `wrong_high` | Factually wrong **and** the customer can act on it and get a bad result | Would a shop owner following this misconfigure something, miss revenue, or break compliance? |
| `wrong_contained` | Factually wrong, but the cost is a wrong expectation rather than a wrong action | Wrong, yet nothing breaks if they believe it |
| `incomplete` | Substantially right, missing a condition that changes the outcome | Usually: the "off" state, a gate upstream, or a limit that makes the feature not apply |
| `correct` | Verified against source | Record the notable ones — credit matters, and it is how you spot a curriculum that *works* |
| `unverifiable` | Depends on tenant config, infrastructure, billing terms or a third party | List it; never guess it |

**Every non-`correct` grade needs a `path:line` on the pinned commit.** `ledger.py` refuses
findings that don't have one. "I remember this being true" is not a grade.

## Fairness rules

These exist because breaking them produces findings that are technically right and unfair,
which destroys the trainer's trust in the whole exercise and is worse than reporting nothing.

1. **Separate transcription noise from error.** Zoom's VTT mangles words. One session was
   transcribed as "the rate, of course, indicates…" where the trainer plainly said "purple" —
   they had said purple/green correctly moments earlier. If a reading only makes sense as a
   mis-transcription, it is not a finding. Check whether they got it right elsewhere in the
   same session before grading.
2. **Credit self-corrections.** "They can only book the day before — I mean, the day after"
   lands on the right answer. Grade the answer they finished on, and say the delivery was
   confusing if it matters.
3. **Credit a trainer who contradicts wrong in-app copy.** Twice now a trainer has been right
   while the product's own popover was wrong. That is a product bug and a point *for* the
   trainer. Never grade someone down for correcting the UI.
4. **Read the label before blaming the person.** Where a trainer's error matches what the
   in-app label or help text says, the finding belongs in `product-bugs.md` and the training
   note is "the label is lying to you", not "you were wrong".
5. **Hedges are good practice.** "I believe it's one hour" is wrong on the number but right
   in form. Correct the fact, note the hedge approvingly, and don't treat it as confident error.
6. **Don't grade opinion.** Benchmarks, coaching targets, "I'd love to see you above 25%",
   competitor claims and pricing are not code. They go in `unverifiable`.
7. **A demo failing is not a training error.** Several findings in the seed set were the
   trainer's environment, not their knowledge. Put those in practice notes, separately from
   accuracy, and say plainly when everything taught from memory was right.

## Model delivery — required on every wrong or incomplete finding

A grade tells the trainer what was wrong; it does not tell them what good sounds like. Every
`wrong_high`, `wrong_contained` and `incomplete` finding carries a `model_delivery` object, and
`ledger.py` refuses the line without one:

```json
"model_delivery": {
  "script": "Leave Explain Delete off. With it off, your advisors get Delete w/ Reason, so every removed campaign records why — that is what you want for reporting.",
  "show": ["Campaigns → Settings", "Point at Explain Delete and leave it unchecked", "Delete a test campaign and show the reason picker"],
  "check": "Ask: if an advisor deletes a campaign tomorrow, where will you see why?"
}
```

- **`script`** — two to four sentences, in the trainer's voice, said to the customer. It states the
  corrected fact *and* the condition the trainer missed (the off branch, the gate, the real
  formula). It must be true on the pinned commit — the same `evidence` backs it.
- **`show`** — the clicks that demonstrate it on screen, using the in-app labels exactly as the
  code renders them. Omit when nothing can be shown.
- **`check`** — one question the trainer can ask to confirm the customer understood.
- Keep `say_instead` as the one-line headline; `model_delivery` is the worked example under it.
- When the finding is a product bug (the label is wrong), the script says how to explain around
  the label until it is fixed — never just "say it right".
- Plain language, no internal jargon, no `path:line` in the script. Write it the way the best
  trainer on the team would say it, not the way the code reads.

## Health check — follow-ups that came out of the session

Every report ends with a **Customer health check**: what the session revealed about the
account across four components, and the follow-ups or tickets someone needs to create. It goes
in the narrative under `health_check`; `build_report.py` renders it.

| component key | what to look for |
|---|---|
| `usage` — Product usage & engagement | How often they log in, which features they actually use vs. ignore, how many of their staff are active, whether their workflow is consistent ("we only use the inbox", "nobody else has logged in", "we stopped sending campaigns") |
| `support` — Support & service activity | Problems raised in the session, recurring issues, open tickets they mention, how long something has been broken, frustration with resolution time |
| `sentiment` — Sentiment & feedback | Praise, frustration, NPS / CSAT comments (CSAT coming soon), direct feedback to the CSM or trainer, "we're thinking about…" |
| `commercial` — Financial & commercial health | Payment or billing issues, renewal or contract talk, expansion interest (more locations, add-ons), whether an owner / exec attended |

Status per component: `healthy`, `watch`, `at_risk`, or `no_signal`. **Most sessions give no
signal on most components — `no_signal` is the honest default.** Never infer a status from
silence, and never upgrade one from a single polite remark.

Sources, in order:
1. **The transcript** — always. Cite the stamp in the signal text.
2. **Zoho Desk / Zoho CRM, read-only, if the tools are available in the run** — open tickets for
   the account (count, severity, age) and renewal / payment status. Say which source each
   signal came from in `source`. If not available, write "transcript only".
3. Never query MongoDB, a customer tenant, or Zoom beyond what the audit already reads.

`followups` lists every action the session generated. One row per action:

| type | when |
|---|---|
| `support_ticket` | Customer reported something broken or misconfigured in their account |
| `bug` | The product behaves wrong or the copy is wrong (also flagged `product_bug` in findings) |
| `feature_request` | Customer asked for something the product does not do |
| `csm_followup` | Account-level concern: churn risk, unhappy stakeholder, expansion interest, low adoption |
| `training_followup` | Trainer promised to send something, re-cover a topic, or schedule another session; or a `wrong_high` finding the customer acted on and needs correcting |
| `billing` | Invoice, payment, contract or pricing question |

Each row: `title`, `detail`, `owner` (Support / Dev / CSM / Training / Billing — a team, not a
person), `priority` (`high` if the customer is blocked, at risk, or was told something
`wrong_high`; else `medium` / `low`), `stamp`, and `existing` (the Desk/Sprints ticket number if
one already covers it, else empty). **Propose only — the audit never creates the ticket.** A
promise the trainer made ("I'll send you that guide") is always a follow-up.

## Where the costly errors actually are

From the seed set, ranked by how often they bit:

1. **The "off" branch.** Trainers describe what a toggle does when on. What happens when it
   is off is where the shop's real decision lives, and it was omitted repeatedly.
2. **Upstream gates.** A feature that only applies for one trigger, one channel, or one DMS
   integration, taught as general. Always check for a launch blocker or an early `return`.
3. **Simplified formulas.** "Six-month average plus 5%" for a weighted blend. If a trainer
   states a calculation, read the calculation.
4. **Inverted booleans.** More than one field's label means the opposite of its behavior.
5. **Name collisions.** "On Deck" means two different things in two places; so does a
   campaign card's counter versus the approval queue.

## claim_id

`<area>.<feature>.<assertion>` — e.g. `campaigns.explain-delete.is-confirmation`,
`analytics.recommended-goals.six-month-average`, `scheduler.after-hours.uploads-files`.

The id is the **join key for repeat detection**, which is the main reason this runs on a
schedule. Rules:

- Reuse an existing id from the ledger when the same misconception recurs, even loosely.
  Two trainers describing after-hours resource links as uploads is *one* claim_id, twice.
- Name the **misconception**, not the feature. `…after-hours.uploads-files` collides with
  itself next time; `…after-hours.resources` does not.
- Never rename an id. It breaks every repeat count that referenced it.
