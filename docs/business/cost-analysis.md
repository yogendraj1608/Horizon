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

Horizon integrates alert correlation and UEBA-based prioritization, reducing analyst workload
