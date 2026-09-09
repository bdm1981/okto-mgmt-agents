# Findings ledger

Append-only. One row per graded claim, oldest first. `claim_id` is the join key:
reuse an existing id when the same misconception recurs, so repeats are
detectable. Written by `scripts/ledger.py`; do not hand-edit rows.

| date | uuid | trainer | claim_id | grade | stamp | evidence |
|---|---|---|---|---|---|---|
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `campaigns.explain-delete.is-confirmation` | wrong_high | 15:04 | dc-user/src/js/common/components/campaigns/DeleteCampaignButton.js:16, dc-user/src/js/common/components/campaigns/OnDeck.tsx:347 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `campaigns.keyword-detection.builds-audience` | wrong_high | 17:47 | dc-user/src/js/admin/components/campaigns/KeywordDetector.tsx:196, dc-server/models/campaign.ts:6 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `campaigns.campaign-schedule.is-general` | wrong_high | 16:22 | dc-server/modules/campaignBuilder.js:5741, dc-server/modules/dispatcher.js:312 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `reports.campaign-attribution.unreleased` | wrong_high | 31:34 | dc-user/src/js/common/components/campaignsV2/featureFlag.ts:25, dc-server/routes/dniImpressions.ts:27 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `reports.dni.shows-sales-conversion` | wrong_contained | 28:01 | dc-user/src/js/admin/components/reports/customer-engagement/widgets/DniTrend/DniLearnMoreModal.tsx:44 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `scheduler.after-hours.resources-are-uploads` | wrong_contained | 40:45 | dc-user/src/js/admin/components/sites/booking/BookingSpecs.tsx:336 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `campaigns.managed-links.counter-needs-active-campaign` | wrong_contained | 26:37 | dc-server/routes/urlshorten.js:10, dc-server/models/UrlShorten.js:50 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `campaigns.managed-links.shows-individuals` | wrong_contained | 25:34 | dc-user/src/js/admin/components/campaigns/CreateShortUrlModal.js:20 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `scheduler.additional-comments.is-text-field` | wrong_contained | 36:00 | dc-user/src/js/admin/components/sites/booking/GlobalSettings.tsx:358 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `campaigns.structured-messages.is-general` | incomplete | 17:10 | dc-server/modules/campaigns/launchBlockers.ts:125, dc-server/modules/campaigns/messageBuilders/messageBuilderUtils.ts:474 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `scheduler.service-hours-duration.single-service` | incomplete | 37:22 | dc-user/src/js/admin/components/sites/booking/BookingSpecs.tsx:138, dc-booking/src/pages/ServiceOptions.tsx:147 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `campaigns.on-deck.card-vs-queue` | incomplete | 21:07 | dc-user/src/js/admin/components/campaigns/CampaignHistory.js:42, dc-server/modules/campaigns/messageBuilders/smsMessageBuilder.ts:462 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `campaigns.optout-zero.means-healthy` | incomplete | 21:07 | dc-server/modules/campaigns/QUESTIONABLE_BUSINESS_DECISIONS.md, dc-server/modules/campaigns/messageBuilders/smsMessageBuilder.ts:136 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `campaigns.message-rotation.randomizes-order` | incomplete | 20:02 | dc-server/modules/campaigns/campaignUtils.ts:414 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `scheduler.short-notice.independent-of-same-day` | incomplete | 42:20 | dc-user/src/js/admin/components/sites/booking/BookingSpecifications.tsx:709 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `scheduler.booking-messages.only-two` | incomplete | 44:34 | dc-user/src/js/admin/components/sites/booking/BookingMessages.tsx:35 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `campaigns.call-campaigns.no-customer-send` | correct | 09:46 | dc-server/modules/campaigns/callCampaigns.js:185 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `campaigns.auto-approve.bypasses-queue` | correct | 11:55 | dc-server/modules/campaignBuilder.js:638, dc-user/src/js/common/components/campaigns/OnDeck.tsx:383 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `scheduler.same-day-off.next-day` | correct | 42:20 | dc-booking/src/components/DatePicker.tsx:58 |
| 2026-08-25 | `uuid:seed-20260825-crm` | CRM trainer | `scheduler.service-caps.per-day-and-slot` | correct | 43:59 | dc-user/src/js/admin/components/sites/booking/ServiceCard.tsx:54 |
| 2026-08-25 | `uuid:seed-20260825-analytics` | Aaron | `analytics.recommended-goals.six-month-average` | wrong_high | 13:32 | dc-user/src/js/admin/components/reports/sales-analytics/goals/GoalWizardShopPage.tsx:387, dc-user/src/js/admin/components/reports/sales-analytics/goals/GoalWizardActorPage.tsx:341 |
| 2026-08-25 | `uuid:seed-20260825-analytics` | Aaron | `analytics.rocket-gauge.every-metric-has-recommendation` | wrong_high | 58:42 | moto-sales-tracker-api/Services/Service/RocketGaugeStaticResponseService.cs:31, dc-user/src/js/admin/components/reports/sales-analytics/widgets/RocketGauge.tsx:61 |
| 2026-08-25 | `uuid:seed-20260825-analytics` | Aaron | `analytics.year-goal.needs-all-twelve` | incomplete | 27:43 | dc-user/src/js/common/hooks/queries/useOverviewReports.ts:140, dc-user/src/js/admin/components/reports/sales-analytics/widgets/OverviewReports/OverviewReportsContainer.tsx:201 |
| 2026-08-25 | `uuid:seed-20260825-analytics` | Aaron | `analytics.goal-colors.three-states` | incomplete | 25:43 | dc-user/src/js/common/utils/overviewGoalColors.ts:12 |
| 2026-08-25 | `uuid:seed-20260825-analytics` | Aaron | `analytics.ticket-ranges.brackets-by-shop-type` | correct | 33:11 | moto-tracker-model/Migrations/Sql/Init/01_create_schema.sql:5520 |
| 2026-08-25 | `uuid:seed-20260825-analytics` | Aaron | `analytics.thresholds.presets` | correct | 26:08 | dc-user/src/js/admin/components/reports/sales-analytics/GoalsThresholdsPage.tsx:52 |
| 2026-08-25 | `uuid:seed-20260825-analytics` | Aaron | `analytics.rocket-gauge.not-ai-generated` | correct | 58:42 | moto-sales-tracker-api/Services/Service/RocketGaugeStaticResponseService.cs:9 |
| 2026-08-25 | `uuid:seed-20260825-analytics` | Aaron | `analytics.sync-intervals.per-dms` | unverifiable | 06:47 | — |
| 2026-08-25 | `uuid:seed-20260825-deepdive` | Aaron | `admin.stale-tasks.unread-are-safe` | wrong_high | 77:47 | dc-server/modules/cleanup.js:657, dc-server/models/tracker.js:37 |
| 2026-08-25 | `uuid:seed-20260825-deepdive` | Aaron | `admin.invite-expiry.one-hour` | wrong_high | 15:25 | dc-server/modules/cognitoService.js:418 |
| 2026-08-25 | `uuid:seed-20260825-deepdive` | Aaron | `scheduler.after-hours.resources-are-uploads` | correct | 55:57 | dc-user/src/js/admin/components/sites/booking/BookingSpecs.tsx:336 |
| 2026-08-25 | `uuid:seed-20260825-deepdive` | Aaron | `reports.dni.shows-sales-conversion` | correct | 41:28 | dc-user/src/js/admin/components/sites/dniDistributionModal/dniDistributionModal.tsx:142 |
| 2026-08-25 | `uuid:seed-20260825-deepdive` | Aaron | `admin.scorecard-bands.80-60` | correct | 79:58 | dc-server/routes/scorecardBuckets.ts:190, dc-server/routes/call.js:1627 |
| 2026-08-25 | `uuid:seed-20260825-deepdive` | Aaron | `admin.sms-allowance.2500-per-plan` | unverifiable | 73:47 | — |
| 2026-08-24 | `uuid:seed-20260824-foundations` | Aaron | `inbox.voicemail-download.admin-only` | wrong_contained | 21:00 | dc-user/src/js/user/components/inbox/VoicemailTask/VoicemailPlayer.tsx:156, dc-user/src/js/admin/components/calls/CallRecordingPlayer/PlayerControls.tsx:95 |
| 2026-08-24 | `uuid:seed-20260824-foundations` | Aaron | `reviews.dedupe.applies-to-campaign-links` | incomplete | 66:15 | dc-server/modules/campaigns/REFACTOR.md:187 |
| 2026-08-24 | `uuid:seed-20260824-foundations` | Aaron | `campaigns.on-deck.card-vs-queue` | incomplete | 41:38 | dc-user/src/js/admin/components/campaigns/CampaignHistory.js:42 |
| 2026-08-24 | `uuid:seed-20260824-foundations` | Aaron | `calls.role-access.by-extension` | correct | 48:55 | dc-user/src/js/admin/components/calls/CallModalTabs/CallModalTabs.tsx:168 |
| 2026-08-24 | `uuid:seed-20260824-foundations` | Aaron | `marketing.only-platform-with-call-campaigns` | unverifiable | 42:41 | — |
| 2026-08-27 | `uuid:wj2mARB6RtWx2Ij1/K/xIw==` | Aaron | `admin.stale-tasks.unread-are-safe` | wrong_high | 74:29 | dc-server/modules/cleanup.js:657-686, dc-server/models/tracker.js:37 |
| 2026-08-27 | `uuid:wj2mARB6RtWx2Ij1/K/xIw==` | Aaron | `admin.invite-expiry.one-hour` | wrong_high | 14:31 | dc-server/modules/cognitoService.js:303,349,418-455 |
| 2026-08-27 | `uuid:wj2mARB6RtWx2Ij1/K/xIw==` | Aaron | `admin.directly-assigned.admins-can-see` | wrong_contained | 30:00 | dc-server/modules/taskVisibility.ts:24-29, dc-server/modules/taskVisibility.ts:61-97, dc-server/routes/messages.js:786-787 |
| 2026-08-27 | `uuid:wj2mARB6RtWx2Ij1/K/xIw==` | Aaron | `admin.disable-user.tasks-marked-unread` | incomplete | 12:28 | dc-server/routes/users.js:460-490, dc-server/models/tracker.js:37,106 |
| 2026-08-27 | `uuid:wj2mARB6RtWx2Ij1/K/xIw==` | Aaron | `scheduler.after-hours.resources-are-uploads` | correct | 54:06 | dc-user/src/js/admin/components/sites/booking/BookingSpecs.tsx:336-437 |
| 2026-08-27 | `uuid:wj2mARB6RtWx2Ij1/K/xIw==` | Aaron | `admin.holiday-types.three` | correct | 43:09 | dc-server/models/holiday.ts:28,44-53 |
| 2026-08-27 | `uuid:wj2mARB6RtWx2Ij1/K/xIw==` | Aaron | `admin.holidays.block-booking` | correct | 43:36 | dc-server/modules/appointment-availability/appointment-availability.service.ts:1275-1314 |
| 2026-08-27 | `uuid:wj2mARB6RtWx2Ij1/K/xIw==` | Aaron | `billing.calls-unlimited` | unverifiable | 69:35 | — |
