# Open product bugs

Found while auditing training, independent of any trainer. Several are the product
contradicting itself — a trainer read the label aloud and the label was wrong.

Status: `open` · `ticketed` · `fixed <sha>`. Add the ticket id when one is filed.

| what | where | effect | status | first seen |
|---|---|---|---|---|
| Stale-task auto-close ignores read state, and only sweeps a ~1-day window | `dc-server/modules/cleanup.js:657` | Unread customer tasks are silently completed; anything aging past the window is never closed, so it cannot drain a backlog. Two separate defects in one query. The training has since stopped promising unread tasks are safe (3 Sep), but the code is unchanged. | open | Deep Dive, 25 Aug 2026 |
| Voicemail download has no role gate | `dc-user/src/js/user/components/inbox/VoicemailTask/VoicemailPlayer.tsx:156` | Advisors can download customer voicemail audio while being blocked from call recordings (`PID 0/5`) and transcripts (`isAdmin`). Inconsistent policy on the same class of recorded audio. | open | Foundations, 24 Aug 2026 — now seen in 7 of 15 August runs |
| "Require Delete Reason" label is inverted | `dc-user/.../campaigns/AddCampaign.js:731` vs `campaignsV2/wizard/steps/DeliveryStep.tsx:324` | Legacy and V2 label the same `explainDelete` field with opposite meanings; behavior matches V2. Enabling the setting a customer asked for *removes* the safeguard they wanted. | open | CRM, 25 Aug 2026 |
| Campaign type popover claims a Call campaign places a phone call | `dc-user/.../campaigns/AddCampaign.js:504` | It creates an inbox `Tracker` task and sends nothing. Two trainers have now had to contradict this help text live. | open | CRM, 25 Aug 2026 |
| "Close their open tasks" toggle does not govern private tasks | `dc-server/routes/users.js:465` vs `:482` | Disabling a user runs a second unconditional `updateMany` that completes every `private:true` task they hold, whatever the toggle says. The toggle is taught — correctly, for shared tasks — as the safeguard against losing a departing advisor's unreturned customer work; user voicemails, personal-number SMS and private faxes are exactly the tasks it silently closes. | open | Deep Dive, 3 Sep 2026 |

## Why this file is in the skill

A bug found here is worth more than the training note that surfaced it. The dashboard reads
this table, and a bug that keeps appearing across sessions is evidence for prioritising it —
"two trainers had to talk around this" is a stronger argument than one bug report.
