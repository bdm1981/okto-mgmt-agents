# Open product bugs

Found while auditing training, independent of any trainer. Several are the product
contradicting itself — a trainer read the label aloud and the label was wrong.

Status: `open` · `ticketed` · `fixed <sha>`. Add the ticket id when one is filed.

| what | where | effect | status | first seen |
|---|---|---|---|---|
| Stale-task auto-close ignores read state, and only sweeps a ~1-day window | `dc-server/modules/cleanup.js:850` (fn `closeStaleTasks` at `:837`) | Unread customer tasks are silently completed; anything aging past the window is never closed, so it cannot drain a backlog. Two separate defects in one query. The training has since stopped promising unread tasks are safe (3 Sep), but the code is unchanged. The window half has now been taught as "anything older than N days gets closed" in **five** sessions across three trainers, most recently Admin Part 2 on 22 Sep — nobody has ever described it correctly, because the setting's own wording invites the wrong reading. **Re-verified 1 Oct 2026 at `4f4044545` — and the citation this table carried was wrong.** `cleanup.js:657` is, and was already on 30 Sep, unrelated ShopWare RO-reconciliation code; the sweep actually lives in `closeStaleTasks` at `:837`. Both halves of the defect are confirmed at `:850`: the query is `{ tenantId, date_updated: { $lte: staleDate, $gte: staleGte } }` — bounded **below** as well as above by `staleGte` (`staleDate` minus one day, `startOf('day')`, `:845-848`), so it is a ~1-day window and anything older is never swept — and it carries no read or `responded` filter of any kind, so unread tasks are completed. `cleanup.js` is byte-identical between `8719ad736` and `4f4044545`. | open | Deep Dive, 25 Aug 2026 |
| Voicemail download has no role gate | `dc-user/src/js/user/components/inbox/VoicemailTask/VoicemailPlayer.tsx:162` | Advisors can download customer voicemail audio while being blocked from call recordings (`PID 0/5`) and transcripts (`isAdmin`). Inconsistent policy on the same class of recorded audio. | open | Foundations, 24 Aug 2026 — now seen in 7 of 15 August runs |
| ~~"Require Delete Reason" label is inverted~~ **FIXED 22 Oct 2026 at `15b4ddb206`** | `dc-user/src/js/admin/components/campaigns/AddCampaign.js:743` (popover `:746`, field `:740`); same label on `EditCampaign.js:1070`, `OnDemandInputs.js:332`, `CallOnDemandInputs.js:239`, `DateCampaignInputs.js:280`; V2 comment `dc-user/src/js/common/components/campaignsV2/api.ts:295` (field `:297`) | Legacy and V2 labelled the same `explainDelete` field with opposite meanings and behaviour matched V2, so enabling the setting a customer asked for *removed* the safeguard they wanted. **The oldest and most-repeated entry in this table: first seen 25 Aug 2026, graded wrong in eleven sessions across three trainers, and never once taught correctly by anyone** — because every trainer was quoting the popover accurately. **Fixed in two commits on 22 Oct 2026** under TRS-I2670 / TRS-I2672 (`ac594162ea`, then `15b4ddb206`): all five legacy screens now read **"Delete queued messages without asking for a reason"**, with a popover that states both branches — "On: this campaign’s queued messages on the On Deck page delete right away, with no option to give a reason. Off: their delete button also offers Delete w/ Reason." `git grep "Require Delete Reason"` at `15b4ddb206` returns the string **only** inside the new regression spec `dc-user/playwright-tests/marketing/legacy-queued-message-delete-label.spec.ts`, which asserts the old label is absent and the new one present. Behaviour is unchanged and was always correct: `DeleteCampaignButton.js:16` still returns a bare trash button when the flag is set and `OnDeck.tsx:347` still renders Delete w/ Reason only when it is false — the lie was the string, and the string is gone. **This is the fix this table asked for** ("port an honest string to the legacy screen", 29 Sep) at the full width the 16 Oct note widened it to (all five screens, `EditCampaign.js` among them). Ledger rows are not rewritten: they were right on their dates. | fixed `15b4ddb206` | CRM, 25 Aug 2026 |
| Campaign type popover claims a Call campaign places a phone call | `dc-user/src/js/admin/components/campaigns/AddCampaign.js:512` | It creates an inbox `Tracker` task and sends nothing. **Four trainers** have now had to contradict this help text live, twice on 23 Sep alone — Advisor Training and CRM Overview, three hours apart, both describing a Call campaign correctly as a task. Corrected again on 28 Sep (CRM Overview) and on 29 Sep (Admin Part 1) — a fifth trainer talking around the same sentence. The training has fully routed around this popover; every trainer on the bench now corrects it unprompted, which is the strongest possible argument that the text, not the people, is the thing to change. | open | CRM, 25 Aug 2026 |
| "Close their open tasks" toggle does not govern private tasks | `dc-server/routes/users.js:484` vs `:505` | Disabling a user runs a second unconditional `updateMany` that completes every `private:true` task they hold, whatever the toggle says. The toggle is taught — correctly, for shared tasks — as the safeguard against losing a departing advisor's unreturned customer work; user voicemails, personal-number SMS and private faxes are exactly the tasks it silently closes. Re-verified 29 Sep at `7790cef49`: the toggle still governs only `private:false` at `:484`, and the unconditional private sweep opens at `:501` (`private: true` at `:505`). | open | Deep Dive, 3 Sep 2026 |
| Call visibility tooltip omits site managers and All Recordings advisors | `dc-user/src/js/admin/components/calls/CallAnalyzerModal/CallAnalyzerModal.tsx:631` | The default-state tooltip reads "Visible to admins and ext owner". Two other audiences see the call: the control itself is gated `roleCheck([0, 5])` at `:733`, which is Administrator **and** Site Manager, and `callsReviewUtils.ts:178-183` unpins any advisor holding **All Recordings** from the extension filter entirely. A trainer reading the tooltip aloud states a narrower rule than the product enforces — which is what happened on 24 Sep, three minutes after the same trainer had given the site-manager rule correctly, and again on 30 Sep (Admin Part 1). Re-verified 30 Sep at `8719ad736`: the string is still at `CallAnalyzerModal.tsx:631` and the extension pin is still lifted for All Recordings advisors — re-sited 9 Oct 2026 at `b9d917bc76`: the helper is `resolveCallsUserExtensionOverride` at `callsReviewUtils.ts:168` and the lift is `:178-183`, **not** the `:150` / `:177` this row has carried. | open | Admin Part 1, 24 Sep 2026 |
| Call transcript "download" is a .txt, and admin-only | `dc-user/src/js/admin/components/calls/CallModalTabs/CallModalTabs.tsx:197` | The button builds a `text/plain` Blob named `call-transcript-<date>.txt`. The trainer described it twice in one session as a PDF export, which is what the surrounding UI implies. It is also gated on `isAdmin` (`:169` at `b9d917bc76`; the `roleCheck([0, 5])` definition is `:144`) — which is `roleCheck([0, 5])`, so Administrator **and** Site Manager, not admin alone — while the voicemail download next to it has no gate at all — the same inconsistent policy on recorded audio recorded above, from the other side. | open | Admin Part 1, 15 Sep 2026 |
| Outrunning Overhead turns green at break-even, not at goal | `dc-user/src/js/admin/components/reports/sales-analytics/widgets/OutrunningOverhead/OutrunningOverhead.tsx:236` | Each day is coloured on `cumulativeDiff` — cumulative gross profit minus overhead — and never compared against the GP goal. It reads green at 92k GP against a 156k goal, while green everywhere else on the same dashboard means *goal met* (`overviewGoalColors.ts`). May be intended (the widget is about overhead, not goals); the defect is one page using one colour for two meanings. **Found live by the trainer**, who told the room it looked wrong and would raise it with the devs. | open | Shop Analytics, 15 Sep 2026 |
| ~~Vendor exclusion from Advisor IQ is retroactive only~~ **WITHDRAWN 9 Oct 2026 — not a bug** | `dc-calls/src/modules/director.js:103` + `:112` → `dc-calls/src/modules/utils.js:526`; `dc-calls/src/routes/events.js:2121` + `:2129` | The entry claimed that marking a contact as a vendor runs a one-time `Call.updateMany` over existing calls and that "nothing in the call-creation path (`dc-server/routes/call.js`) ever consults the Vendor collection", so every later call is created `vendor: false` and re-enters Advisor IQ. The one-time sweep is real (`vendors.js:30`) and the dc-server statement is literally true — **and irrelevant, because dc-server does not ingest calls.** The only `Call.create` in `dc-server/routes/call.js` is the `manualUpload` path (`:2426`). Live telephony is ingested by **dc-calls**, which gates on vendors twice, independently: `director.js` calls `utils.vendorLookup(contactNumber, siteInfo.tenantId)` unconditionally on every call (`:103`) and sets `detail.vendor = isVendor` (`:112`) before `Call.create(detail)` (`:118`), where `vendorLookup` queries `Vendors.findOne({tenantId, number: e164Number})` (`utils.js:526`) against the same `vendors` collection dc-server writes (`dc-calls/src/models/vendor.js` binds `mongoose.model("Vendor", VendorSchema, "vendors")`); and the transcription pipeline runs its **own** lookup at `events.js:2052`, logs "Detected vendor call", and skips Advisor IQ, scorecards and sentiment wholesale behind `if (!isVendor)` at `:2060`. So future calls from a vendor number are both flagged `vendor: true` and never scored, and `scorecardsReport.ts:125` (`vendor: { $ne: true }`) then excludes them. `vendorLookup` has been in this path since **July 2025** (`ae54c2c92d` / `262895f5c9`), i.e. fourteen months before the bug was raised — it was never true. Same service-boundary error as the withdrawn `/bookings/capture` entry, and the most expensive one yet: this was the most-repeated finding in the ledger, and it inverts the grading on **13 rows across 4 trainers**. Flagged for a human; grade rows not rewritten. **Re-sited 17 Oct 2026 at `ea1c07a280`:** `events.js` gained 75 lines (a fix to `processTranscription`'s label handling, unrelated to the vendor gate), shifting both citations 54 lines down to `:2052` and `:2060`. The gate itself is unchanged, so the withdrawal stands. **Re-sited again 18 Oct 2026 at `3e9a53ec13`:** `events.js` moved a second consecutive run, +97/−28 under commit `aa24eb36f6` (TRS-I2678 — BDC copies of outbound calls now receive durations, transcript and summary; the hunk nearest the gate mirrors a transcript-only call onto its BDC copies before the analysis write). Again unrelated to the vendor gate, which is unchanged in substance: `vendorLookup` at `:2118`, the "Detected vendor call" log at `:2121`, and `if (!isVendor)` at `:2129`. Two runs in a row in which this file moved for reasons that touch no row in this table — the withdrawal stands. | withdrawn | raised 17 Sep 2026, withdrawn 9 Oct 2026 |
| "Disable Campaigns" says SMS, but switches off every channel | `dc-user/src/js/user/components/inbox/ActionMenu/CampaignModal.tsx:83` vs `:55` | The modal's help text reads "This will remove this customer from future **SMS** campaigns." The action writes a single global flag, `{ campaigns: false }`, and every audience builder gates on it without regard to channel — `campaignBuilder.js:4627` (`cust.campaigns !== false`) and `campaignUtils.ts:298`. An advisor choosing the reason "No longer wants text messages" silently ends that customer's email and voice marketing too, and nothing in the UI says so. **A third write path was found on 23 Sep and it is the quietest one:** choosing the `optout` outcome in `CampaignOutcomeModal.js:25` writes the same global `{ campaigns: false }`. That modal appears automatically whenever an advisor completes any campaign task, carries no help text at all, and the dropdown entry reads as a note about this message. In the 23 Sep CRM session the customer's entire outcome chart was opt-outs — every one of which switched that contact off across all channels. **Allie now corrects this live** — on 22 Sep she read the label aloud and told the room it was wrong, one day after being graded incomplete for repeating it. The training has routed around the bug; the bug is still there. **Re-sited 6 Oct 2026 at `c2962ec29`: the audience-builder citation this row carried, `campaignBuilder.js:4357`, was never that code at any baseline on record** (checked at `8719ad736`, `4f4044545`, `565dea231`, `926cb3888` and `c2962ec29`) — the gate is `:4509` at `cae072fa9`, under the comment block at `:4502`; `campaignUtils.ts` is at `:187`, **not** the `:109` this row carried on 6 Oct, which was itself wrong. **Re-sited again 9 Oct 2026 at `b9d917bc76`** — both files changed in the 33 commits since `56b95236f1`: the audience gate is now `campaignBuilder.js:4627` (comment block `:4620`) and `campaignUtils.ts:298`. **Re-sited 13 Oct 2026 at `6ad7e2a008`: the gate is `campaignBuilder.js:4638` (comment block `:4631`) and `campaignUtils.ts:301`.** **Re-sited 16 Oct 2026 at `50e2beab68`: the gate is `campaignBuilder.js:4673` (comment block `:4666`); `campaignUtils.ts:301` is unmoved.** Four re-sites in three weeks on one row — these two files move most runs, so re-resolve before quoting rather than trusting the stored line. Behaviour unchanged, bug stands. | open | Advisor Training, 21 Sep 2026 |
| ~~Scheduler exit-intent bailout capture posts to a route that does not exist~~ **WITHDRAWN 28 Sep 2026 — not a bug** | `dc-booking/src/utils/api.js:12` → `graphql-broker/src/routes/index.ts:39` | The 24 Sep entry said `POST /bookings/capture` had no handler "anywhere in dc-server". That is true and irrelevant: `dc-booking`'s `REACT_APP_API_URL` points at **graphql-broker**, not dc-server. The route exists at `graphql-broker/src/routes/booking/capture.ts:62`, is mounted at `/bookings` (`routes/index.ts:39`), has its own test suite, and calls `generateLead` (`capture.ts:125`) which posts to dc-server's `customer/createLead`. All three bail-out paths (`StayOrGo.js:74`, `SkipToForm.js:50`, `Header.tsx:139`) work. The finding was a service-boundary error, not a product defect. Re-verified 7 Oct 2026 at `cae072fa9`: `routes/index.ts:39` still mounts `/bookings` and `capture.ts` still handles it — the withdrawal stands. | withdrawn | raised 24 Sep 2026, withdrawn 28 Sep 2026 |

## Full re-verification sweep — 1 Oct 2026 at `4f4044545`

No session was gradeable on this run (every recording in the window is transcript-less), so the run spent its
time re-resolving every citation in this table against the day's baseline instead. **All ten open bugs are still
open.** Nothing was fixed and nothing was withdrawn. Seven of the ten citations had drifted:

| bug | was | is now |
|---|---|---|
| stale-task auto-close | `cleanup.js:657` | `cleanup.js:849` (fn at `:836`) — the old line was never this code |
| voicemail download no gate | `VoicemailPlayer.tsx:156` | `:162` |
| Require Delete Reason inverted | `AddCampaign.js:731` | `:732` (`DeleteCampaignButton.js:16` unchanged) |
| close-open-tasks vs private | `users.js:465` / `:482` | `:484` / `:505` (unconditional sweep opens at `:501`) |
| call transcript download | `CallModalTabs.tsx:194` | `:197` (`text/plain` Blob at `:192`) |
| Outrunning Overhead colour | `OutrunningOverhead.tsx:219` | `:236` — still keyed on `cumulativeDiff` alone, never on the goal |
| vendor exclusion retroactive | `vendors.js:29` | `:30` — still a one-time `Call.updateMany` over existing calls |

Unchanged and re-confirmed verbatim: `AddCampaign.js:504` (the Call-campaign popover, still claiming a phone
call), `CallAnalyzerModal.tsx:631` ("Visible to admins and ext owner"), `CampaignModal.tsx:55` and `:83` (the
SMS wording over a global `{ campaigns: false }` write), and `DeleteCampaignButton.js:16`.

The lesson is the `:657` row: a citation can be stale for days without anything noticing, because the file still
exists and the line number still resolves to *something*. Re-resolve, do not re-quote — and on a day with no
transcripts this sweep is the most useful work available.

## Re-verification sweep — 22 Oct 2026 at `15b4ddb206` — the first row this table has ever closed

**Thirteen commits** landed between `4cdf1bf5f5` and this baseline. No session was gradeable (both of the
day's held sessions recorded without a transcript), so the run swept the table — and for the first time since
25 August a bug came back **fixed** rather than re-sited.

Of the twenty-six cited paths, **twenty were byte-identical** and six moved, and all six moved for the same
reason: TRS-I2670 / TRS-I2672 relabelled the legacy `explainDelete` switch on every screen that carries it
(`AddCampaign.js`, `EditCampaign.js`, `OnDemandInputs.js`, `CallOnDemandInputs.js`, `DateCampaignInputs.js`,
each +5/−3) plus `campaignsV2/api.ts` (+39/−13, unrelated queued-view paging). Nothing else in the table
changed, so **every other citation carries over with certainty and the eight remaining open bugs all stand**.

Three things worth keeping from the close:

- **The fix matched the widened scope.** The 16 October note found the label on five screens after a year of
  this row citing one, and argued that a fix scoped to `AddCampaign.js` would leave four screens lying. The
  shipped fix touches all five. That note is the reason the close is clean rather than partial, and it is the
  clearest return this table has produced on the "grep a UI string across the whole package" rule.
- **Verify a close by the absence of the string, not by the presence of the new one.** `git grep` for the old
  label at the new baseline is one call and it is what proves no screen was missed; reading the new label on
  the screen the row happens to cite proves only that one screen.
- **A regression spec is part of the evidence.** `legacy-queued-message-delete-label.spec.ts` asserts the old
  wording is gone, so this row cannot silently re-open. Note it in the row — a close backed by a test is
  stronger than a close backed by a line number, which is all most of these rows could ever offer.

Also landing this window and bearing on the **ledger** rather than this table: TRS-I2729 (`173abef7b5`) adds a
callback-number gate to `dc-server/routes/customer.ts:809` — `if (!validateNumberForImport(req.body.number).valid)`
returns 204 before any contact or tracker is written. `scheduler.appointment-lead.phone-is-minimum`, the
third-largest curriculum defect in the ledger (nine rows, Aaron and Allie), asserted exactly that gate; the
12 October note established there was none. **The claim is now true from `173abef7b5` forward.** Per the
standing rule the nine rows are not rewritten — they were right on their dates — but the defect is closed by
the product, not by coaching, and the training script should now be checked for the opposite error.

**Keep pipe tables out of this file** — `build_dashboard.py` splices every markdown pipe-row here into the
dashboard's bug table. This section is deliberately prose-only.

## Why this file is in the skill

A bug found here is worth more than the training note that surfaced it. The dashboard reads
this table, and a bug that keeps appearing across sessions is evidence for prioritising it —
"two trainers had to talk around this" is a stronger argument than one bug report.

## Re-verification sweep — 2 Oct 2026 at `565dea231`

No session was gradeable again (quiet Friday — no training scheduled), so the run re-verified the table
against a fresh baseline. **All ten open bugs are still open.** Nothing fixed, nothing withdrawn.

Method changed from the 1 Oct sweep and is better: compare the **blob hash** of each cited file between
the previous baseline and this one. 29 commits landed on `development` between `4f4044545` and
`565dea231`, and **every one of the thirteen cited files is byte-identical across the two**, so every
line number in this table carries over with certainty — no re-reading required, and no risk of the
`:657`-style rot that cost the 1 Oct run, because an identical blob cannot have drifted.

Files confirmed byte-identical `4f4044545` → `565dea231`: `dc-server/modules/cleanup.js`,
`VoicemailPlayer.tsx`, `AddCampaign.js`, `DeleteCampaignButton.js`, `campaignsV2/api.ts`,
`dc-server/routes/users.js`, `CallAnalyzerModal.tsx`, `callsReviewUtils.ts`, `CallModalTabs.tsx`,
`dc-server/routes/vendors.js`, `dc-server/models/call.js`, `CampaignModal.tsx`,
`graphql-broker/src/routes/index.ts`.

**One citation corrected.** The call-visibility row cites `callsReviewUtils.ts:179`; the file's full path
is `dc-user/src/js/admin/components/calls/Calls/callsReviewUtils.ts`, **not** under `common/utils/`. The
All Recordings check is confirmed at `:179` (`permission.label === "All Recordings"`). This surfaced only
because the path was spelled out and checked for existence — a `git diff` over a misspelled path returns
empty and reads exactly like "unchanged". Verify each path resolves before trusting a quiet diff.

## Baseline unchanged — 4 Oct 2026, still `565dea231`

Third consecutive run on the same commit. An explicit HTTPS fetch of `development` returned `565dea231` and
`git rev-list --count 565dea231..FETCH_HEAD` was `0`, so the baseline is the same object the 2 Oct sweep
verified this table against. Nothing below can have drifted and there is no diff to read; per the 3 Oct note,
that is an identity argument, not a re-check, and it is stated as such.

The part that does have work in it was run: `git cat-file -e "$SHA:$PATH"` over **all twenty-two cited
paths** (the thirteen from the 2 Oct sweep plus `campaignsV2/api.ts`, `CallAnalyzerModal.tsx`,
`CallModalTabs.tsx`, `OutrunningOverhead.tsx`, `CampaignModal.tsx`, `booking/capture.ts`,
`scorecardsReport.ts`, `campaignBuilder.js`, `campaignUtils.ts`, `CampaignOutcomeModal.js`,
`overviewGoalColors.ts`, `taskHelper.js`, `messages.js`). **All twenty-two resolve.** No misspelled path is
hiding behind an empty diff this time. All ten open bugs remain open; nothing fixed, withdrawn or re-sited.

Note `pin_baseline.sh` again printed `fetch failed` and fell back to the local `origin/development`. It
happened to be right, because nothing had moved — but the fallback is silent about *why* it is right. Fetch
explicitly by URL and compare, as the 30 Sep note says; the agreement is what makes the fallback trustworthy,
not the fallback itself.

## Re-verification sweep — 5 Oct 2026 at `926cb3888`

The first run in four with a moving baseline: **19 commits** landed between `565dea231` and `926cb3888`, so this
is a real blob-hash sweep rather than the identity argument the 3 and 4 Oct runs had to settle for.

**All ten open bugs remain open.** Nothing fixed, withdrawn or re-sited. All twenty-five cited paths resolve at
this commit (`git cat-file -e` on each), and every file cited by the table above is **byte-identical** between
`565dea231` and `926cb3888`, so every line number in it carries over with certainty — no re-reading required.
Spot-checked anyway by identifier rather than by line, per the 1 Oct rule: `closeStaleTasks` is still at
`cleanup.js:836` with the bounded-below query at `:849`, and `vendors.js:30` is still the single
`Call.updateMany` over existing calls.

Exactly one cited file changed across the 19 commits, and it is **not** in the bug table:
`dc-server/modules/taskHelper.js`, which carries the `inbox.message-search.open-only` ledger citations.
Commit `dba26529f` deleted two unrelated lines, shifting the contact branch from `:172` to `:169` and the
message branch from `:255` to `:254`. Behaviour unchanged.

Two process notes worth keeping with the table. First, `pin_baseline.sh` fell back silently to a local
`origin/development` that was **seven commits stale** (`a6feb10f0`); the explicit HTTPS fetch is what produced
`926cb3888`, and unlike the last three runs the difference was real. Second, the abbreviated citation
`campaignsV2/api.ts:284` expands to `dc-user/src/js/**common**/components/campaignsV2/api.ts`, not `admin/` —
guessing `admin/` makes the existence check report a missing file and reads like a deletion. Three other
abbreviated paths in this table sit under a different parent than the obvious guess; resolve with
`git ls-tree -r --name-only $SHA | grep "/<basename>$"` before concluding anything.

**Keep pipe tables out of this file.** Per the 3 Oct note, `build_dashboard.py` scrapes *every* markdown pipe-row
in `product-bugs.md` into the single "Open product bugs" table on the dashboard, so a sub-table here renders as
malformed rows there. This section is deliberately prose-only.

## Re-verification sweep — 6 Oct 2026 at `c2962ec29`

**27 commits** landed between `926cb3888` and this run's baseline, the largest single-day movement since the
sweeps began. **All ten open bugs remain open.** Nothing fixed, withdrawn or re-sited on the merits. Of the
twenty-two cited paths checked, twenty were byte-identical across the two commits and two moved:
`dc-server/modules/campaignBuilder.js` (+40/−4, every changed line a comment about Date campaigns) and
`dc-server/modules/campaigns/campaignUtils.ts`. Neither change touches the logic any bug row describes.

**The finding that matters is a method correction, not a code change.** The 5 Oct sweep concluded from blob
identity that "every line number in the table carries over with certainty". Blob identity proves a citation has
not *drifted*; it proves nothing about a citation that was **already wrong**. `campaignBuilder.js:4357`, carried
by the "Disable Campaigns" row, has never pointed at the `cust.campaigns !== false` audience gate at any baseline
on record — at today's it is a `params.ro.customer.fname` assignment. The gate is at `:4505`. This is the second
rotted citation found by searching for the identifier rather than reading the line, after `cleanup.js:657` on
1 Oct, and in both cases the cited line resolved to plausible-looking code, which is why neither was caught sooner.
Hash-compare to find what moved; `git grep` the distinguishing identifier to confirm the citation still names the
right thing. Both, every time.

Spot-checked by identifier at this baseline, all unchanged in behaviour: `closeStaleTasks` at `cleanup.js:836`
with the bounded-below query at `:849` and `staleGte` at `:844`; `vendors.js:30` still the single `Call.updateMany`
over existing calls; `CampaignModal.tsx:55` (`{ campaigns: false }`) against `:83` ("future **SMS** campaigns");
`CallAnalyzerModal.tsx:631` ("Visible to admins and ext owner"); `CallModalTabs.tsx:192` (`text/plain`) and `:197`
(the `.txt` filename); `OnDeck.tsx:347` (`{!campaign?.explainDelete && (`).

Two path traps repeated from earlier runs, both caught by `git cat-file -e` before anything was concluded.
`OnDeck.tsx` is under `dc-user/src/js/common/components/**campaigns**/`, not `campaignsV2/`, despite sitting beside
a `campaignsV2/api.ts` citation in the same table cell — the 5 Oct lesson, second instance. And `campaignUtils.ts`
is `dc-server/modules/campaigns/campaignUtils.ts`, a server file, not a `dc-user` one.

Process note for whoever writes the next sweep: on this host the shell is **zsh**, which does not word-split
unquoted variables, so `for p in $PATHS` over a multi-line string iterates **once** with the whole blob. Use
`while IFS= read -r p` over a heredoc.

**Keep pipe tables out of this file** — per the 3 Oct note, `build_dashboard.py` splices every markdown pipe-row
here into the dashboard's bug table. This section is deliberately prose-only.

## Re-verification sweep — 7 Oct 2026 at `cae072fa9`

**43 commits** landed between `c2962ec29` and this baseline, the largest movement yet. **All ten open bugs
remain open.** Nothing fixed, withdrawn or re-sited on the merits. Of the twenty-one cited paths swept,
nineteen are byte-identical across the two commits; two moved, and neither change touches any logic a bug row
describes: `dc-server/modules/campaignBuilder.js` and `graphql-broker/src/routes/index.ts`.

**A third rotted citation, and the hash sweep could not have caught it.** The "Disable Campaigns" row carried
`campaignUtils.ts:109`, written into this file by the 6 Oct sweep. That file is **byte-identical** between
`c2962ec29` and `cae072fa9`, so hash comparison says "nothing can have drifted" — and the line was wrong when
it was written. `git grep 'campaigns !== false'` resolves it to a single occurrence at **`:187`**. This is the
same shape as `cleanup.js:657` (1 Oct) and `campaignBuilder.js:4357` (6 Oct): plausible-looking code at the
cited line, nobody looks again. Note the extra turn of the screw here — the rot was introduced *by a sweep
whose job was to fix rot*, which is an argument for the grep being mandatory on every row every time rather
than only on rows whose file changed.

Re-sited this run: `campaignBuilder.js` `:4505` → **`:4509`** (comment block `:4498` → `:4502`);
`campaignUtils.ts` `:109` → **`:187`**; `routes/index.ts` `:37` → **`:39`** on the withdrawn bail-out row.

Spot-checked by identifier at this baseline, all unchanged in behaviour: `closeStaleTasks` at `cleanup.js:836`
with the bounded-below query at `:849` and `staleGte` at `:844`; `vendors.js:30` still the single
`Call.updateMany` over existing calls, and `dc-server/routes/call.js` still contains **zero** references to the
Vendor collection; `CampaignModal.tsx:55` (`{ campaigns: false }`) against `:83` ("future **SMS** campaigns");
`CallAnalyzerModal.tsx:631` ("Visible to admins and ext owner"); `CallModalTabs.tsx:192` (`text/plain`);
`OutrunningOverhead.tsx:42` still deriving `cumulativeDiff` from GP minus overhead with no goal comparison;
`DeleteCampaignButton.js:16` and `OnDeck.tsx:347`.

Two bug rows gained fresh evidence from this run's sessions rather than from the code. The Call-campaign
popover was contradicted live for a sixth time (CRM Overview, 10:12 — "Voice is the only type that does not
send automatically... it will generate a task to your inbox"), and the Disable Campaigns SMS wording was
contradicted live for the third audited session running (Advisor, 22:43). Both rows' case is now that every
trainer on the bench routes around the string, which is the strongest available argument for changing it.

**Keep pipe tables out of this file** — `build_dashboard.py` splices every markdown pipe-row here into the
dashboard's bug table. This section is deliberately prose-only.

## Re-verification sweep — 9 Oct 2026 at `b9d917bc76`

Quiet Friday (no training scheduled, nothing gradeable), so the run re-verified the whole table
against a fresh baseline. **One bug withdrawn, nine still open.**

33 commits landed between `56b95236f1` and `b9d917bc76`. Blob-hashing every cited path found
**two** changed files, both cited by the Disable-Campaigns row: `campaignBuilder.js` and
`campaignUtils.ts`. The audience gate moved `:4509` → `:4627` and `campaignUtils.ts` `:187` → `:298`;
behaviour unchanged. Every other cited file is byte-identical across the two baselines.

Per the 6 Oct rule, blob identity was **not** treated as proof — each bug's distinguishing
identifier was also grepped at the new baseline. That caught two citations that had been wrong
independently of any drift: the All-Recordings extension-pin lift is `callsReviewUtils.ts:178-183`
(helper at `:168`), not the `:150` / `:177` the table carried; and the transcript-download `isAdmin`
gate is `:169`, not `:168`. Both corrected in place.

**The withdrawal is the real result.** "Vendor exclusion from Advisor IQ is retroactive only" was
the most-repeated finding in the ledger — nine sessions, five trainers — and it was never true.
It is the third instance of the service-boundary error first recorded on 28 Sep for
`/bookings/capture`: the original grep was scoped to `dc-server/routes/call.js`, concluded "nothing
in the call-creation path consults the Vendor collection", and never asked which service actually
ingests calls. It is **dc-calls**, and it gates on vendors twice over. See gotchas.md,
"The vendor-exclusion bug was never real".

## Re-verification sweep — 10 Oct 2026 at `c7206d9b17`

Quiet Saturday (no training scheduled Fri–Sun, nothing gradeable, nothing recovered from the gap), so
the run re-verified the whole table again. **Nine bugs still open, both withdrawals stand, nothing fixed
and nothing newly withdrawn — the first fully clean sweep this table has had.**

9 commits landed between `b9d917bc76` and `c7206d9b17`, every one of them provisioning or
sa-to-ce-migrator work nowhere near a bug surface. Blob-hashing found **all 22 cited paths
byte-identical**.

Per the 6 Oct rule that blob identity is not proof, each bug's distinguishing identifier was grepped
afresh anyway. All of them resolve exactly where the table says:

| bug | identifier grepped | resolves at |
|---|---|---|
| stale-task auto-close | `closeStaleTasks`, `staleGte` | `cleanup.js:836`, query `:849`, bound `:844` |
| voicemail download no gate | `roleCheck` / `isAdmin` / `PID` | **no match in the file** — the gate's absence, stated positively |
| Require Delete Reason inverted | `explainDelete` | `AddCampaign.js:732`, `DeleteCampaignButton.js:16`, `OnDeck.tsx:347`, `api.ts:284` |
| Call-campaign popover | `"sent as a phone call"` | `AddCampaign.js:504` |
| close-open-tasks vs private | `private: false` / `private: true` | `users.js:484` / `:505` |
| call visibility tooltip | `"Visible to admins and ext owner"`, `roleCheck([0, 5])` | `CallAnalyzerModal.tsx:631` / `:733` |
| All-Recordings extension lift | `resolveCallsUserExtensionOverride`, `hasAllRecordings` | `callsReviewUtils.ts:168`, lift `:178-183` |
| transcript download | `text/plain`, `call-transcript-`, `isAdmin` | `CallModalTabs.tsx:192` / `:197` / `:169` (def `:144`) |
| Outrunning Overhead colour | `cumulativeDiff` | `OutrunningOverhead.tsx:236` |
| Disable Campaigns | `campaigns: false`, `campaigns !== false`, `optout` | `CampaignModal.tsx:55`/`:83`, `CampaignOutcomeModal.js:18`/`:25`, `campaignBuilder.js:4723` (comment `:4716`), `campaignUtils.ts:302` |

**The voicemail row is worth noting as a method.** Its defect is the *absence* of a gate, so there is
no identifier to resolve — the check is that `VoicemailPlayer.tsx` contains no `roleCheck`, `isAdmin`
or `PID` reference at all. An empty grep is normally a warning sign (see the 9 Oct note on case
sensitivity); here it is the evidence, which only holds because the file was confirmed byte-identical
first. Pair the two checks or neither means anything.

**Two inline citations repaired in place.** The call-visibility row carried `callsReviewUtils.ts:150`
in its body text *and* the 9 Oct note correcting it to `:178-183` in the same sentence; the
Disable-Campaigns row did the same with `:4505`/`:109` against `:4627`/`:298`. A re-site note appended
to a row does not fix the wrong number earlier in that row, and a reader quoting the row gets whichever
one they reach first. **When re-siting, edit the citation, then append the note — not just the note.**

Also repeated from 5, 6 and 9 Oct: `pin_baseline.sh` reported `fetch failed` and fell back to a local
`origin/development` at `b9d917bc76` that was **9 commits stale**. The explicit HTTPS fetch produced
the baseline above. That fallback has now been wrong on four of the last six runs.

## Re-verification sweep — 16 Oct 2026 at `50e2beab68`

Quiet Friday (no training runs Fri–Sun), nothing gradeable, nothing recovered from the 27-row coverage
gap, so the run re-verified the whole table. **Nine bugs still open, both withdrawals stand, nothing
fixed and nothing newly withdrawn** — but this was *not* a clean sweep: **49 commits** landed between
`8903277f91` and `50e2beab68`, and **six rows carried stale line numbers**, four of which had been
stale since before the previous run.

Blob comparison over the 26 cited paths: **24 byte-identical, 2 changed** —
`dc-server/routes/call.js` (+38, the new `/callbacks` route for the inbox Callback badge, TRS-I2556)
and `dc-user/src/js/common/components/campaignsV2/api.ts` (+152/−46).

| bug | was &rarr; is now | drifted when |
|---|---|---|
| stale-task auto-close | `cleanup.js:849` &rarr; `:850`; fn `:836` &rarr; `:837`; bound `:844-847` &rarr; `:845-848` | before 15 Oct |
| Require Delete Reason inverted | `AddCampaign.js:732` &rarr; `:740`; popover `:742` &rarr; `:744`; `api.ts:284` &rarr; comment `:288` / field `:290` | label before 15 Oct, `api.ts` this window |
| Call-campaign popover | `AddCampaign.js:504` &rarr; `:512` | before 15 Oct |
| close-open-tasks vs private | inline `:465` / `:483` &rarr; `:484` / sweep opens `:501`, `private: true` `:505` | before 15 Oct |
| vendor exclusion (withdrawn) | `call.js:2305` &rarr; `:2426`; `utils.js:542` &rarr; `:526`; `events.js:1992` / `:2003` &rarr; `:1998` / `:2006` | before 15 Oct |
| Disable Campaigns | `campaignBuilder.js:4673` &rarr; `:4723`; comment `:4666` &rarr; `:4716`; `campaignUtils.ts:301` &rarr; `:302` | this window |

Confirmed unmoved and re-grepped by identifier: `VoicemailPlayer.tsx:162` (and still **no** `roleCheck`,
`isAdmin` or `PID` anywhere in the file — the absence *is* the bug, and it only means anything because the
file was confirmed byte-identical first), `CallAnalyzerModal.tsx:631` / `:733`,
`callsReviewUtils.ts:168` with the lift at `:178-183`, `CallModalTabs.tsx:192` / `:197` / `:169` (def `:144`),
`OutrunningOverhead.tsx:236`, `CampaignModal.tsx:55` / `:83`, `CampaignOutcomeModal.js:18` / `:25`,
`DeleteCampaignButton.js:16`, `OnDeck.tsx:347`, `vendors.js:30`,
`director.js:103` / `:112` / `:118`, `capture.ts:125`, `routes/index.ts:39`.

### The Require Delete Reason bug got sharper, and five times wider

Two findings on the row that has produced more wrong_highs than any other label in this table.

**1. The product now documents the true behaviour in code while the label keeps lying.** The comment in
`campaignsV2/api.ts` was rewritten in this window:

```
- // explainDelete = require a reason when deleting the campaign.
+ // explainDelete = a queued message is removed without asking for a reason.
```

That is the correct semantics, and it matches `DeleteCampaignButton.js:16` — `if (deleteOnly ||
campaign?.explainDelete)` returns a bare trash button with no reason modal. So a developer has now written
the right meaning down. The user-facing label and popover are untouched: `label="Require Delete Reason"`
with "If enabled, users will be required to provide a reason when deleting this campaign"
(`AddCampaign.js:741` / `:744`). The gap between the code comment and the UI string is no longer an
inference from behaviour — the repository states both readings explicitly, in two files, at the same commit.

**2. The lying label is on five screens, not one.** This table has only ever cited `AddCampaign.js`.
Every one of these binds `name="explainDelete"` to the same inverted label:

| file | name | label |
|---|---|---|
| `dc-user/src/js/admin/components/campaigns/AddCampaign.js` | `:740` | `:741` |
| `dc-user/src/js/admin/components/campaigns/EditCampaign.js` | `:1067` | `:1068` |
| `dc-user/src/js/admin/components/campaigns/OnDemandInputs.js` | `:329` | `:330` |
| `dc-user/src/js/admin/components/campaigns/CallOnDemandInputs.js` | `:236` | `:237` |
| `dc-user/src/js/admin/components/campaigns/DateCampaignInputs.js` | `:277` | `:278` |

`EditCampaign.js` matters most of the five: editing an existing campaign is the path a shop takes *after*
a trainer has explained the setting, so it is where a customer acts on the wrong reading. A fix that
changes only `AddCampaign.js` leaves four screens lying, which is worth stating on the ticket.

**Method note.** Both findings came out of the *changed*-file half of the blob comparison, not the
unchanged half. The 6 Oct rule says blob identity is not proof and to re-grep every identifier anyway;
the converse is the cheaper win and was not written down — **when a cited file has changed, read the diff
for meaning, not just for the new line number.** `api.ts` would have passed a line-number-only re-site
silently, and the comment rewrite is the most interesting thing this table has learned in a fortnight.

## Re-verification sweep — 18 Oct 2026 at `3e9a53ec13`

A quiet Sunday (no training runs Fri–Sun), so the run's work went here. **Six commits** landed since the
17 Oct baseline `ea1c07a280`, so this is a real blob-hash sweep rather than an identity argument.

**All open bugs remain open. Nothing was fixed, withdrawn or re-opened.** Of the cited paths, every one is
byte-identical across the two baselines except **`dc-calls/src/routes/events.js`**, which belongs to the
*withdrawn* vendor row and is re-sited above.

Per the 6 Oct rule that byte-identity is not proof, the distinguishing identifier of each row was grepped
afresh rather than inferred from an unchanged hash, and all of them land where this table says:
`closeStaleTasks` at `cleanup.js:837`; `name="explainDelete"` on all **five** screens at
`AddCampaign.js:740`, `EditCampaign.js:1067`, `OnDemandInputs.js:329`, `CallOnDemandInputs.js:236` and
`DateCampaignInputs.js:277`, with `OnDeck.tsx:347` and the honest V2 comment at `campaignsV2/api.ts:288`
(field `:290`); the audience gate at `campaignBuilder.js:4673` under its comment block at `:4666`, with
`campaignUtils.ts:301` and the third write path at `CampaignOutcomeModal.js:25`.

**One process finding, and it is about this file rather than the code.** Three of the abbreviated citations
here resolve to a different parent than the obvious guess, and all three were guessed wrong in one pass this
run before `git ls-tree` settled them:

- `campaignUtils.ts` → **`dc-server/modules/campaigns/`** (not under `dc-user/.../campaignsV2/`)
- `CampaignOutcomeModal.js` → **`dc-user/src/js/user/components/tasks/`** (not `admin/components/campaigns/`)
- `OnDeck.tsx` → **`dc-user/src/js/common/components/campaigns/`** (not `campaignsV2/`)

Each wrong guess makes `git cat-file -e` report a missing file, which reads exactly like a deletion — the
failure mode the 5 Oct note names. This is now the fourth, fifth and sixth instance of it. The fix is not
another reminder to be careful: **write the full path into the row the first time it is resolved**, so the
next sweep greps a path instead of reconstructing one.

### 21 October 2026 — one cited file moved, and the diff is unrelated to any row here

**17 commits** landed between `c6c7466e39` and `4cdf1bf5f5`. Blob-hashing every cited path found **thirty
byte-identical and one changed**: `dc-server/modules/campaignBuilder.js` (+3/&minus;1), cited by the
Disable-Campaigns row. Per the 16 October rule the diff was read rather than just renumbered, and it is
`testSMS` now passing its body through `appendOptOutFooter` so a test send reads exactly as a real one
does — nothing to do with the global `campaigns: false` flag this row is about. The gate itself is
unchanged in substance and is re-sited to `campaignBuilder.js:4723` (comment block `:4716`), with
`campaignUtils.ts` moving one line to `:302`.

**The Require Delete Reason row took its eleventh session this run** (CRM Overview, 21 October), which is
the most-repeated finding in the ledger and the clearest case in this table of a trainer being graded wrong
for reading the product's own label aloud. **Nine open bugs stand, both withdrawals stand, nothing was fixed
or recovered.**
