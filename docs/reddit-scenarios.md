# Reddit Data Quality test runner

One browser-capable Render cron service (`snoocommerce-browser-traffic`) runs
all scenarios. It sends Reddit events only. The storefront's Meta/TikTok
integrations remain available; this runner does not invoke them.

| Pixel | Event | Source | Budget |
| --- | --- | --- | --- |
| a2_ibjroms8g8bo | ViewContent | Pixel | 20/run |
| a2_ibjroms8g8bo | Search | CAPI | 20/run |
| a2_ibjroms8g8bo | AddToCart | Dual, shared conversion ID | 20 logical events/run |
| a2_ibjroms8g8bo | Contact | CAPI | 20/run |
| a2_ibjroms8g8bo | SnooTestAlpha / Snoo Test Beta | Custom, CAPI | 20 each/run |
| a2_ibjroms8g8bo | AddToWishlist | CAPI, null score | 5/day |
| p2_17hhlij2ehubf | Search + Lead | CAPI, low KDF | 10,001 Search + 1 Lead/day |

Contact needs the pixel's lead-gen feature enabled. Do not interpret a hidden
event as dispatch failure. Custom events use `type.tracking_type=CUSTOM` and
`type.custom_event_name`; validate both exact names in detail API calls.

## Preview and configuration

Run from `server/`; preview never loads a browser or sends network requests:

```sh
python3 manage.py run_reddit_scenarios --mode rapid
python3 manage.py run_reddit_scenarios --mode daily
```

The execution command is `python manage.py run_reddit_scenarios --execute`.
Set REDDIT_FIRST_PIXEL_TOKEN privately for the main pixel and
REDDIT_ACCESS_TOKEN for the KDF pixel. Set REDDIT_PIXEL_ID=a2_ibjroms8g8bo
and REDDIT_TEST_KDF_PIXEL_ID=p2_17hhlij2ehubf. If REDDIT_FIRST_PIXEL_TOKEN is absent,
the main pixel also uses REDDIT_ACCESS_TOKEN; that requires a token with
access to both pixels. Optional REDDIT_TEST_EMAIL supplies one SHA-256 email baseline; it
does not guarantee a positive match score. No random click IDs are generated.

## Cadence and budgets

Rapid mode: set REDDIT_TEST_MODE=rapid and cron schedule `*/5 * * * *`.
Daily mode: set REDDIT_TEST_MODE=daily and cron schedule `10 21 * * *`.
Update BOTH settings when switching; keeping the five-minute schedule in
daily mode still starts containers and consumes runtime.

AddToWishlist and the KDF pixel are sent only in the daily five-minute slot,
21:10–21:14 UTC by default, in either mode. Set REDDIT_TEST_DAILY_UTC=HH:MM
on a five-minute boundary to move it; also align the daily cron schedule.
Choose an upcoming slot before starting rapid testing to populate those
cases promptly, then keep it fixed. There is no extra seeding command.

Five AddToWishlist events/day means 35 events over seven full days, or at
most 40 across eight calendar dates. This budget assumes one scheduled run
per slot, no other AddToWishlist sender and no old traffic still in the window.
IDs are deterministic for retries and shared across the dual pair. There is
no persistent ledger on Render cron; repeated manual runs rely on ingestion
deduplication, so do not manually retrigger the daily slot or move the slot
after it has run. Never treat IDs alone as proof of a global hard quota.

The KDF batch creates >10,000 total events immediately, with one Lead that
day. With daily runs, 7–8 Leads remain below 10 in the inspected lookback;
the ratio also remains below the legacy 0.1% threshold. Do not send other
KDF events to this pixel. API rollup delay still applies. The larger batch
uses eleven requests of at most 1,000 events; it does not require thousands
of browser journeys. No automatic retries occur after failures.

## Deployment and migration

1. Deploy the frontend first and confirm `/reddit-test.html` serves the
   standalone harness, not the storefront's catch-all route.
2. Suspend the old `snoocommerce-traffic` hourly cron in Render. Removing it
   from render.yaml does not establish that the deployed service stopped.
3. Reuse `snoocommerce-browser-traffic`; set its Docker command to
   `python manage.py run_reddit_scenarios --execute` if an old override exists.
   Sync its environment and five-minute schedule from render.yaml. Verify
   the web backend deploy includes the ViewContent CAPI suppression.
4. Inspect the first successful run, then verify Events Manager/API rollups.
   Disable old browser deployments/manual generators before judging channel
   isolation. Historical CAPI ViewContent rows can persist until they age out.
5. After testing, change the SAME service to daily mode and daily schedule.
   Do not create another cron or an always-on worker.

No live deployment or ingestion acceptance is established by local tests.
Dispatch logs report transport success, not scoring or processing acceptance.
Verify the main pixel's source mix, both custom names, Contact visibility,
dual deduplication, populated summary/detail consistency, AddToWishlist's
null score with <100 events, and pixel-wide KDF advice without event filters.
Repeat final acceptance against deployed native V4/nested API. Existing
V3 flat results do not establish V4 acceptance. Nonzero scoring still needs
realistic, accepted test identities; this runner does not promise it.
