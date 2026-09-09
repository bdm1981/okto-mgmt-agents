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
