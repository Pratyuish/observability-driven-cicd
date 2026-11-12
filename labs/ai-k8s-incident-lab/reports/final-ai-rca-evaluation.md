# Final AI-Assisted Kubernetes RCA Evaluation

**Project:** Observability-Driven CI/CD — AI Kubernetes Incident-to-PR Lab  
**Evaluation status:** Evidence-based case study, **not a controlled AI accuracy or MTTR benchmark**  
**Environment:** Local Kind cluster `kind-ai-incident-lab`, namespace `ai-incidents`  
**Report date:** 12 November 2026  
**Public repository:** https://github.com/Pratyuish/observability-driven-cicd

## Executive summary

Five controlled Kubernetes incident scenarios were investigated with a read-only, AI-assisted RCA workflow, followed by explicit, manually executed remediation and verification. **All five lab workloads passed the reported recovery checks**. The findings are suitable for a reproducible technical showcase, provided the difference between evidence-based diagnosis, demonstration recovery, and measured AI performance remains explicit.

- **5/5** incidents have documented RCA findings and reported lab recovery validation.
- **4/5** RCA cases (INC-002–INC-005) were reviewed against uploaded Kubernetes evidence; INC-001 rests on previously shared command outputs and recovery narrative, not a raw original evidence package included in the publication inputs.
- **No independent blind ground-truth scoring experiment** was run; do **not** report “100% AI RCA accuracy” as a benchmark.
- **No manual/AI investigation duration, actual incident-to-recovery MTTR, token consumption, or provider cost** was consistently instrumented; improvements and costs remain **not measured**.
- Prior GitHub Actions `CI/validate` runs were reported passing. The status of checks after the *final* publication commit has not been verified in this report.

## Scope and methodology

1. Deploy isolated workloads, inject/retain intentionally faulty configurations.
2. Capture pod status, Deployment configuration, events, container logs, and collection time as available.
3. Review each `ai-input.txt` as **untrusted evidence**; cite a filename and distinguish symptoms from causes.
4. Recommend fixes but keep diagnosis read-only; require human review before Kubernetes changes or PR merge.
5. Apply manually approved fixes in local Kind; verify Kubernetes readiness plus application/functional checks where available.
6. Record missing measurements instead of imputing them.

**Evaluation unit:** one incident *case*, not multiple independent AI model trials. Confidence judgments in individual RCA outputs are subjective and have **not** been statistically calibrated.

## Incident-by-incident case review

| ID | Supported diagnosis | Recovery observation | Caveat |
|---|---|---|---|
| INC-001 | Readiness endpoint misconfiguration (previous investigation) | 1/1 ready and 20/20 sampled HTTP requests succeeded | Raw original input was not re-audited here; success samples are post-fix only |
| INC-002 | OOMKilled due to 128 MiB bytearray allocation under 32Mi limit | Deployment 1/1; most recent termination exit 0 `Completed` | No peak-memory time series; Deployment restarts a naturally terminating script |
| INC-003 | Mandatory `missing-app-config` ConfigMap absent | Deployment 1/1; 0 restarts; ConfigMap present, 2 entries | No reported HTTP end-to-end check |
| INC-004 | Failed service hostname DNS lookup causes unhandled Python exit | 1/1; 0 restarts; 15 reported HTTP 200 dependency checks | Original evidence did not prove absent Service; fix also changed client behavior |
| INC-005 | Unresolvable image registry hostname blocks image pull | 1/1; 0 restarts; NGINX HTTP 200 | Recovery uses substitute demo image; original application function not validated |

### Specific source anchors and diagnostic limits

**INC-001:** User-reported Deployment 1/1 and 20/20 HTTP successes; `reports/inc-001-validation.md` was reportedly committed. Original before-fix input was not part of the available attachments for this package; cannot independently verify a full RCA trail.

**INC-002:** `pods.json` reports `OOMKilled`, exit `137`, 174 restarts, `CrashLoopBackOff`; `deployment.yaml` defines `bytearray(128*1024*1024)` and `limits.memory: 32Mi`. Later user output reports a running 1/1 pod with exit `0` (`Completed`) after a revised 256Mi limit. The reported prior run ended earlier than the script's nominal 300-second sleep; do not infer exact execution time or memory footprint.

**INC-003:** `pods.json` and `events.json` explicitly state `configmap "missing-app-config" not found`; `deployment.yaml` references it through `envFrom.configMapRef` with `optional: false`. User verified 1/1 pod Ready, 0 restarts, and ConfigMap with 2 entries after creation.

**INC-004:** `inc-004-...-app-previous.log` reports `socket.gaierror: [Errno -2] Name does not resolve` and `urllib.error.URLError`; `pods.json` reports exit `1` and 178 restarts. User's post-fix output includes 15 successive `Dependency HTTP status: 200` lines and a 1/1 Ready pod with 0 restarts. Root cause of the missing DNS record vs cluster DNS broader state is not independently established in the original capture.

**INC-005:** `pods.json` / `events.json` identify `registry.invalid/ai-lab/missing-app:v1` and `lookup registry.invalid ... no such host`; pod had `ImagePullBackOff` and zero restarts. User verified replacement `nginx:1.27` 1/1 Ready, 0 restarts, HTTP 200. Registry image metadata beyond the failed hostname was not reachable.

## Evaluation scorecard and KPI definitions

| KPI | Result | How to interpret |
|---|---:|---|
| Cases investigated | 5 | Five distinct simulated scenarios |
| Lab scenarios with reported recovery success | 5/5 | Observational pass, not production service availability |
| Cases with uploaded diagnostic evidence reviewed in this evaluation | 4/5 | INC-002 through INC-005 |
| Cases with independently blinded RCA scoring | 0/5 | Known fault narratives were available; no blinded benchmark |
| Post-fix HTTP checks INC-001 | 20/20 | Limited post-fix sample |
| Post-fix HTTP checks INC-004 | 15/15 | 15 success log lines shown |
| Post-fix HTTP check INC-005 | HTTP 200 | One curl response reported |
| AI vs manual investigation time saving | Not measured | Timers and manual control not instrumented |
| AI usage tokens / provider cost | Not measured | No model usage telemetry was collected |
| Production MTTR improvement | Not established | Local fault-injection lab only |

**Important denominator rule:** No HTTP sampling is reported for INC-002 or INC-003. Do not combine the three HTTP results into an overall per-incident SLO or claim uninterrupted availability during faults.

## Evidence quality and safety assessment

**Strengths:** explicit Pod/Deployment state, causal error messages for INC-002–INC-005, captured logs and events where containers started, and human-observed post-fix checks. Evidence supports causes at the *immediate failure mechanism* level.

**Gaps:** source datasets were assembled after faults had been running; some Kubernetes events are aggregated/time-limited; original INC-001 file not available in this package; remediation reviews do not include long-term load tests, staged rollbacks, business transactions or provider cost metrics. No immutable evidence hash ledger was supplied.

**Approval model:** AI generated RCA and *recommendations only*. Any modifications to Kubernetes resources and any GitHub merges require explicit human authorization. Raw events, environment variables, account identifiers, secrets, and service tokens should not be published without review and sanitization.

## Recommendations for version 2

1. Instrument `fault_injected_at`, `evidence_collection_started_at`, `rca_submitted_at`, `fix_applied_at`, `ready_at`, and `http_verified_at` from one monotonic clock where possible, with clearly defined intervals.
2. Run a blinded benchmark: present anonymized evidence without scenario names or injected-fault hints; score exact diagnosis against a locked ground-truth key **after** inference.
3. Add a separate independent manual SRE control and measure time/correctness under similar conditions.
4. Capture model, model version, token usage, per-call cost, retries, and prompt/response identifiers without storing secrets.
5. Publish a validation matrix: schema/dry-run, static/security gates, cluster readiness, API success, canary/rollback, and explicit human approval.
6. Use safe manifest fixtures, synthetic services, and no production data; keep original faulty manifests unchanged for reproductions.

## Publication decision

**Appropriate to publish:** a local Kind, human-approved, AI-assisted incident triage and remediation demonstration with **five reported recovery validations**.  
**Do not claim:** production-proven autonomous remediation, 100% blinded RCA accuracy, quantified MTTR reduction, cost savings, or production SLO improvements.
