# QUALIFICATION07 offline Git checkpoint

This checkpoint depends on PR #2 and targets `review/d1-preauth01-offline-20261023-a601` at `09eae12e950d156e1e8fbbfa294ce9b06e6758b4`. It is a draft review snapshot, not a merge, release, stable tag, device result or D1 acceptance.

REV1 developer FAIL remains intact. Only exact REV2 and the tester's nine independent offline groups passed. D1 remains NOT_PASSED and M0 NOT_STARTED. Historical FAIL/UNKNOWN/once and old return-unproven objects remain untouched. No new product/SDK/device/native-route/Gradle/media tests occur during this Git checkpoint.

`source-whitelist.json` records 694 exact source/report/metadata paths and their original byte hashes; `exclusions.json` records 302 excluded frozen entries plus scope-wide exclusions. Full local manifests remain unmodified and deliberately reference artifacts omitted from Git. A Git checkout cannot independently reproduce all historical binaries or local runtime dependencies.

The selected subset contains owned Q07 tools, schemas, configuration, small text input/metadata, REV1/REV2 status evidence, independent tester drivers/reports and the approved coordination snapshot. The authoritative current phase is the top of CURRENT_DESIGN_BASELINE and MILESTONE_COORDINATION; earlier milestone phase descriptions retain their historical wording.

Excluded: raw/encoded original streams, ZIP/media/native binaries, large generated text, ambient host environment snapshots, runtime/third-party distributions/cache, reserved Windows names, credentials, the tester's copied old06 product sources, other old product trees except two exact static DELIVERY reports, and all new floating real-facts-handoff01 outputs. Exclusions affect Git only; no local artifact is deleted or moved.

Pre-stage review found no credential/private-key pattern hits. Existing license/NOTICE/SBOM material is unchanged; no new third-party distribution is included. `core.autocrlf=false`; staged Git blobs are checked against exact selected source bytes. Frozen source whitespace is retained as evidence rather than edited to satisfy style checks.

Inventory/exclusion/review/scope files and the stage-freezer are bookkeeping outside the inventory's self-hash cycle. Their exact hashes, together with all payload hashes, are captured in the separate local `stage-freeze.json` before staging. Post-commit/ref/PR receipts remain local to avoid circular commit-hash claims.
