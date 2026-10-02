# Open product bugs

Found while auditing training, independent of any trainer. Several are the product
contradicting itself — a trainer read the label aloud and the label was wrong.

Status: `open` · `ticketed` · `fixed <sha>`. Add the ticket id when one is filed.

| what | where | effect | status | first seen |
|---|---|---|---|---|
| Stale-task auto-close ignores read state, and only sweeps a ~1-day window | `dc-server/modules/cleanup.js:849` (fn `closeStaleTasks` at `:836`) | Unread customer tasks are silently completed; anything aging past the window is never closed, so it cannot drain a backlog. Two separate defects in one query. The training has since stopped promising unread tasks are safe (3 Sep), but the code is unchanged. The window half has now been taught as "anything older than N days gets closed" in **five** sessions across three trainers, most recently Admin Part 2 on 22 Sep — nobody has ever described it correctly, because the setting's own wording invites the wrong reading. **Re-verified 1 Oct 2026 at `4f4044545` — and the citation this table carried was wrong.** `cleanup.js:657` is, and was already on 30 Sep, unrelated ShopWare RO-reconciliation code; the sweep actually lives in `closeStaleTasks` at `:836`. Both halves of the defect are confirmed at `:849`: the query is `{ tenantId, date_updated: { $lte: staleDate, $gte: staleGte } }` — bounded **below** as well as above by `staleGte` (`staleDate` minus one day, `startOf('day')`, `:844-847`), so it is a ~1-day window and anything older is never swept — and it carries no read or `responded` filter of any kind, so unread tasks are completed. `cleanup.js` is byte-identical between `8719ad736` and `4f4044545`. | open | Deep Dive, 25 Aug 2026 |
| Voicemail download has no role gate | `dc-user/src/js/user/components/inbox/VoicemailTask/VoicemailPlayer.tsx:162` | Advisors can download customer voicemail audio while being blocked from call recordings (`PID 0/5`) and transcripts (`isAdmin`). Inconsistent policy on the same class of recorded audio. | open | Foundations, 24 Aug 2026 — now seen in 7 of 15 August runs |
| "Require Delete Reason" label is inverted | `dc-user/.../campaigns/AddCampaign.js:732` vs `campaignsV2/api.ts:284` | Legacy and V2 label the same `explainDelete` field with opposite meanings; behavior matches V2. Enabling the setting a customer asked for *removes* the safeguard they wanted. **Sixth wrong_high from this one label** (Admin Part 1, 29 Sep) and it has never once been taught correctly by anyone. The clearest evidence it is the product's fault: trainers read the popover at `AddCampaign.js:742` out loud almost word for word. Coaching cannot fix a trainer who is quoting the UI accurately. Re-verified 29 Sep at `7790cef49`: `DeleteCampaignButton.js:16` still returns a bare trash button when the flag is set, and `OnDeck.tsx:347` still renders the control only when it is false. Note the old V2 citation `DeliveryStep.tsx:324` **no longer exists** at this commit — the honest wording now lives in the comment at `campaignsV2/api.ts:284`. Port an honest string to the legacy screen. | open | CRM, 25 Aug 2026 |
| Campaign type popover claims a Call campaign places a phone call | `dc-user/.../campaigns/AddCampaign.js:504` | It creates an inbox `Tracker` task and sends nothing. **Four trainers** have now had to contradict this help text live, twice on 23 Sep alone — Advisor Training and CRM Overview, three hours apart, both describing a Call campaign correctly as a task. Corrected again on 28 Sep (CRM Overview) and on 29 Sep (Admin Part 1) — a fifth trainer talking around the same sentence. The training has fully routed around this popover; every trainer on the bench now corrects it unprompted, which is the strongest possible argument that the text, not the people, is the thing to change. | open | CRM, 25 Aug 2026 |
| "Close their open tasks" toggle does not govern private tasks | `dc-server/routes/users.js:484` vs `:505` | Disabling a user runs a second unconditional `updateMany` that completes every `private:true` task they hold, whatever the toggle says. The toggle is taught — correctly, for shared tasks — as the safeguard against losing a departing advisor's unreturned customer work; user voicemails, personal-number SMS and private faxes are exactly the tasks it silently closes. Re-verified 29 Sep at `7790cef49`: the toggle still governs only `private:false` at `:465`, and the unconditional private sweep is now at `:483`. | open | Deep Dive, 3 Sep 2026 |
| Call visibility tooltip omits site managers and All Recordings advisors | `dc-user/.../CallAnalyzerModal/CallAnalyzerModal.tsx:631` | The default-state tooltip reads "Visible to admins and ext owner". Two other audiences see the call: the control itself is gated `roleCheck([0, 5])` at `:733`, which is Administrator **and** Site Manager, and `callsReviewUtils.ts:150` unpins any advisor holding **All Recordings** from the extension filter entirely. A trainer reading the tooltip aloud states a narrower rule than the product enforces — which is what happened on 24 Sep, three minutes after the same trainer had given the site-manager rule correctly, and again on 30 Sep (Admin Part 1). Re-verified 30 Sep at `8719ad736`: the string is still at `CallAnalyzerModal.tsx:631` and `callsReviewUtils.ts:177` still lifts the extension pin for All Recordings advisors. | open | Admin Part 1, 24 Sep 2026 |
| Call transcript "download" is a .txt, and admin-only | `dc-user/src/js/admin/components/calls/CallModalTabs/CallModalTabs.tsx:197` | The button builds a `text/plain` Blob named `call-transcript-<date>.txt`. The trainer described it twice in one session as a PDF export, which is what the surrounding UI implies. It is also gated on `isAdmin` (`:168`) — which is `roleCheck([0, 5])`, so Administrator **and** Site Manager, not admin alone — while the voicemail download next to it has no gate at all — the same inconsistent policy on recorded audio recorded above, from the other side. | open | Admin Part 1, 15 Sep 2026 |
| Outrunning Overhead turns green at break-even, not at goal | `dc-user/.../widgets/OutrunningOverhead/OutrunningOverhead.tsx:236` | Each day is coloured on `cumulativeDiff` — cumulative gross profit minus overhead — and never compared against the GP goal. It reads green at 92k GP against a 156k goal, while green everywhere else on the same dashboard means *goal met* (`overviewGoalColors.ts`). May be intended (the widget is about overhead, not goals); the defect is one page using one colour for two meanings. **Found live by the trainer**, who told the room it looked wrong and would raise it with the devs. | open | Shop Analytics, 15 Sep 2026 |
| Vendor exclusion from Advisor IQ is retroactive only | `dc-server/routes/vendors.js:30` vs `dc-server/models/call.js:111` | Marking a contact as a vendor runs a one-time `Call.updateMany` over their **existing** calls. Nothing in the call-creation path (`dc-server/routes/call.js`) ever consults the Vendor collection, so every later call from that number is created `vendor: false`, is scored by Advisor IQ and re-enters the scorecards report (`scorecardsReport.ts:125`). Taught — reasonably — as the way to keep parts suppliers out of advisor scoring. Now **nine sessions across five trainers** and still the most-repeated finding in the ledger. **Taught correctly for the first time on 28 and 30 Sep** (Advisor Training, Allie): “it will not remove future calls, so you'd probably constantly have to mark them as a vendor” — the right reading of the code and the right operational advice. On the morning of 30 Sep the opposite was taught in Admin Part 1 (“any future calls will not be used with Advisor IQ”), graded **wrong_high**: the first time this claim has been stated as a forward-looking guarantee rather than merely omitted. Re-verified 30 Sep at `8719ad736`: `vendors.js:29` still sweeps existing calls once and no call-creation path consults the Vendor collection. That a correct script now exists on a recording strengthens the case for fixing it — the honest version of this feature is awkward to teach, which is why it took nine sessions to say out loud. | open | Advisor Training, 17 Sep 2026 |
| "Disable Campaigns" says SMS, but switches off every channel | `dc-user/.../inbox/ActionMenu/CampaignModal.tsx:83` vs `:55` | The modal's help text reads "This will remove this customer from future **SMS** campaigns." The action writes a single global flag, `{ campaigns: false }`, and every audience builder gates on it without regard to channel — `campaignBuilder.js:4357` (`cust.campaigns !== false`) and `campaignUtils.ts:107`. An advisor choosing the reason "No longer wants text messages" silently ends that customer's email and voice marketing too, and nothing in the UI says so. **A third write path was found on 23 Sep and it is the quietest one:** choosing the `optout` outcome in `CampaignOutcomeModal.js:25` writes the same global `{ campaigns: false }`. That modal appears automatically whenever an advisor completes any campaign task, carries no help text at all, and the dropdown entry reads as a note about this message. In the 23 Sep CRM session the customer's entire outcome chart was opt-outs — every one of which switched that contact off across all channels. **Allie now corrects this live** — on 22 Sep she read the label aloud and told the room it was wrong, one day after being graded incomplete for repeating it. The training has routed around the bug; the bug is still there. | open | Advisor Training, 21 Sep 2026 |
| ~~Scheduler exit-intent bailout capture posts to a route that does not exist~~ **WITHDRAWN 28 Sep 2026 — not a bug** | `dc-booking/src/utils/api.js:12` → `graphql-broker/src/routes/index.ts:37` | The 24 Sep entry said `POST /bookings/capture` had no handler "anywhere in dc-server". That is true and irrelevant: `dc-booking`'s `REACT_APP_API_URL` points at **graphql-broker**, not dc-server. The route exists at `graphql-broker/src/routes/booking/capture.ts:62`, is mounted at `/bookings` (`routes/index.ts:37`), has its own test suite, and calls `generateLead` (`capture.ts:125`) which posts to dc-server's `customer/createLead`. All three bail-out paths (`StayOrGo.js:74`, `SkipToForm.js:50`, `Header.tsx:139`) work. The finding was a service-boundary error, not a product defect. Re-verified 29 Sep 2026 at `7790cef49`: `routes/index.ts:37` still mounts `/bookings` and `capture.ts` still handles it — the withdrawal stands. | withdrawn | raised 24 Sep 2026, withdrawn 28 Sep 2026 |

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
