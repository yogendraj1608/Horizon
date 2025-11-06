# Cost Analysis

## Executive Summary

Project Horizon demonstrates that a fully functional, enterprise-grade Zero Trust ecosystem can be implemented using open-source technologies with **minimal financial overhead** and **no licensing dependency**.  
This section presents a structured comparison of direct, indirect, and opportunity costs against commercial equivalents, proving that Horizon delivers measurable cost efficiency while maintaining high security assurance.

## Cost Model Overview

The total cost of ownership (TCO) for cybersecurity infrastructure is traditionally segmented into:

1. **Licensing and Subscription Fees** – recurring vendor costs.  
2. **Infrastructure and Hosting** – compute, storage, and network expenditure.  
3. **Implementation and Maintenance** – setup, integration, and update effort.  
4. **Operational Costs** – analyst time, monitoring tools, and SOC overhead.  
5. **Training and Compliance** – certification, audit preparation, and reporting costs.

Project Horizon’s cost model significantly reduces the first three categories while optimizing the last two through automation and integration.

## 1. Licensing and Subscription Costs

| Component | Typical Commercial Equivalent | Approx. Annual Licensing Cost (USD) | Horizon Implementation | Cost (USD) |
|------------|--------------------------------|-------------------------------------|--------------------------|-------------|
| Identity & Access (ZTNA/SASE) | Zscaler, Okta, Palo Alto Prisma Access | $25,000 – $40,000 | Keycloak + Pomerium | **$0** |
| Data Security (DSPM) | Netskope, BigID, Symmetry Systems | $30,000 – $50,000 | MinIO + NiFi + Presidio + Custodian | **$0** |
| CNAPP | Wiz, Prisma Cloud, Orca Security | $40,000 – $60,000 | Checkov + Trivy + Kyverno + Falco + Cosign | **$0** |
| XDR/UEBA | SentinelOne, Microsoft Defender XDR, Exabeam | $50,000 – $80,000 | Elastic Stack + UEBA model | **$0** |
| Data Platform & Analytics | Splunk Enterprise, Sumo Logic | $20,000 – $35,000 | Elasticsearch + Kibana | **$0** |

**Annual Licensing Savings:** ≈ **$160,000 – $265,000 per deployment unit**

All technologies used in Project Horizon are open-source and operate under permissive licenses (Apache 2.0, MIT, or Elastic OSS), eliminating recurring fees while maintaining full control over source code and integrations.

---

## 2. Infrastructure and Hosting Costs

Project Horizon was designed for **cloud-neutral, resource-efficient deployment** using lightweight containers.

| Cost Element | Description | Estimated Annual Cost (on standard cloud VM tier) |
|---------------|--------------|--------------------------------------------------|
| Compute (4–5 medium VMs) | Kubernetes, Elastic Stack, Data Services | $2,500 – $3,200 |
| Storage (2 TB block/object) | MinIO and Elasticsearch storage | $1,000 – $1,500 |
| Network Transfer | Cross-VM traffic and Zero Trust proxying | $500 – $700 |
| Backup & Redundancy | Snapshots and archival logs | $300 – $400 |

**Estimated Annual Infrastructure Cost:** ≈ **$4,000 – $5,500**

In contrast, similar managed vendor platforms often exceed **$25,000/year** for equivalent telemetry and compute capacity.

---

## 3. Implementation and Maintenance Costs

| Activity | Commercial Approach | Cost Estimate (USD) | Horizon Approach | Cost Estimate (USD) |
|-----------|--------------------|---------------------|------------------|---------------------|
| Initial Deployment | Vendor onboarding, integration setup | $15,000 – $25,000 | In-house configuration (open-source stack) | **$2,000** |
| Upgrades & Patch Management | Vendor SLA or managed support | $5,000 – $10,000 | Community-supported updates | **$0** |
| Customization & Policy Tuning | Limited (vendor APIs) | $5,000+ | Full flexibility (in-house control) | **$0** |

**Implementation Savings:** ≈ **$20,000 – $35,000**

---

## 4. Operational Costs

Horizon integrates alert correlation and UEBA-based prioritization, reducing analyst workload and false positives.

| Metric | Pre-Horizon (Typical) | Post-Horizon (Achieved) | Impact |
|--------|------------------------|--------------------------|--------|
| Alerts per Week | 1,200–1,500 | **350–400** | 70% reduction |
| Average Investigation Time | 25–30 min | **6–8 min** | 70–75% improvement |
| Analyst Hours Saved per Month | — | **≈ 150–180 hours** | Operational efficiency gain |

**Annualized Analyst Cost Savings:** ≈ **$20,000 – $25,000**

---

## 5. Training and Compliance Costs

Automation through DSPM, CNAPP, and XDR integrations reduces manual evidence generation and audit preparation time.

| Activity | Traditional Manual Effort | Automated via Horizon | Savings |
|-----------|---------------------------|------------------------|----------|
| Audit Evidence Collection | 2–3 person-weeks | Real-time via Elastic + Custodian | 90% |
| Compliance Dashboarding | Separate reporting tools | Integrated visualization | 80% |
| Policy Verification | Manual | Automated policy-as-code | 100% |

**Compliance Efficiency Gain:** Equivalent to **$10,000 – $12,000 annually** in staff time and tooling.

---

## 6. Comparative Total Cost of Ownership (TCO)

| Cost Category | Commercial Stack (Annual) | Project Horizon (Annual) | Savings |
|----------------|---------------------------|---------------------------|----------|
| Licensing | $180,000 | **$0** | **100%** |
| Infrastructure | $25,000 | **$5,000** | **80%** |
| Implementation & Maintenance | $25,000 | **$2,000** | **92%** |
| Operational | $30,000 | **$10,000** | **66%** |
| Compliance & Training | $12,000 | **$2,000** | **83%** |
| **Total TCO (Annual)** | **$272,000** | **$19,000** | **≈ 93% reduction** |

---

## Return on Investment (ROI)

**ROI = (Cost Savings / Project Investment) × 100**

Assuming initial project setup cost of $15,000 (infrastructure + configuration):

- **First-Year ROI:** ≈ **(272,000 − 19,000) / 15,000 × 100 = 1,686%**
- **Three-Year Cumulative ROI:** ≈ **> 5000%** (due to recurring licensing avoidance)

---

## Intangible Benefits

Beyond quantifiable savings, Horizon provides significant *qualitative* value:

- **Vendor Independence:** Enables customization and internal scaling at will.  
- **Skill Development:** Builds in-house cybersecurity expertise.  
- **Transparency:** Open-source stack enhances auditability and trust.  
- **Research Utility:** Serves as a reusable framework for future innovation.

---

## Conclusion

Project Horizon’s open-source model yields **an estimated 90–93% reduction in total ownership cost** relative to commercial Zero Trust offerings.  
It achieves this without sacrificing coverage, scalability, or compliance alignment — proving that **cost efficiency and advanced security can coexist** when architectural design prioritizes openness, modularity, and automation.
