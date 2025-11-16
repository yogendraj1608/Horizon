# **Project Horizon: Unified Zero Trust Architecture**

> **Division:** Security Engineering & Research (SER)  
> **Department:** Cybersecurity, Data Engineering, and Applied Threat Intelligence    
> **Status:** MVP – Functional Prototype Completed  
> **Classification:** Open-Source, Free-Tier Enterprise Security Platform  

---

## **1. Overview**

**Project Horizon** is an end-to-end open-source implementation of a **Zero Trust Security Architecture (ZTSA)** unifying multiple cybersecurity domains — Identity, Data, Workloads, and Detection — into a cohesive and auditable framework.

The project validates the **technical and strategic feasibility** of achieving enterprise-grade Zero Trust enforcement using **community and free-tier tools** only.  
The MVP integrates five solution pillars into a **single telemetry-driven ecosystem**, backed by a centralized **ELK-based detection backbone**, with the ability to scale toward a production-ready platform.

---

## **2. Core Objectives**

- **Zero Trust Enforcement:** Enforce identity-driven access control and eliminate implicit trust.  
- **Centralized Visibility:** Correlate authentication, network, and data events under unified observability.  
- **Data Protection:** Discover, classify, and govern sensitive data at rest and in motion.  
- **SOC Modernization:** Deliver advanced detection engineering and alert automation.  
- **Open Scalability:** Design modular components that can scale across hybrid and cloud environments.

---

## **3. Technical Architecture**

| Layer | Purpose | Key Components |
|-------|----------|----------------|
| **Access & Identity** | Secure, identity-aware access perimeter | Keycloak, Pomerium, pfSense, Suricata |
| **Data Security & Governance** | Sensitive data discovery, classification, and remediation | MinIO, NiFi, Presidio, Cloud Custodian, PostgreSQL |
| **Workload Protection** | Build-time and runtime container security | Kyverno, Cosign, Trivy, Checkov, Falco |
| **Detection & Response** | Centralized telemetry, rule-based & ML-driven detection | Elastic Stack, UEBA Model, Tines |
| **Analytics & Engagement** | Behavioral analytics and proactive simulation | CDP Engine, Python, Mailgun, Elastic |

Each component contributes to the **Zero Trust control loop** of verification, enforcement, and telemetry correlation.

---

## **4. Solution Pillars**

| Pillar | Description | Reference |
|--------|--------------|------------|
| **ZTNA & SASE** | Identity-based perimeter using Keycloak + Pomerium, integrated with Suricata on pfSense. | `/docs/technical/ZTNA - Horizon.pdf` |
| **Customer Data Platform (CDP)** | Behavioral analysis and churn prediction integrated with ELK observability. | `/docs/technical/CDP - Horizon.pdf` |
| **Data Security Posture Management (DSPM)** | Automated data discovery and policy enforcement via Presidio + Custodian. | `/docs/technical/DSPM - Horizon.pdf` |
| **Cloud-Native Application Protection Platform (CNAPP)** | Kubernetes IaC, image signing, and runtime defense (Kyverno, Falco, Trivy). | `/docs/technical/CNAPP - Horizon.pdf` |
| **XDR & Insider Risk Analytics** | Unified detection and UEBA anomaly model for SSH and behavioral events. | `/docs/technical/XDR - Horizon.pdf` |

Each technical document includes architecture diagrams, configuration references, validation results, and evidence of deployment.

---

## **5. Deployment Topology**

| VM | Role | Key Services |
|----|------|---------------|
| **IAM-VM** | Identity and perimeter control | Keycloak, Pomerium, pfSense, Suricata |
| **DSPM-VM** | Data governance and classification | NiFi, Presidio, Cloud Custodian, MinIO |
| **CNAPP-VM** | Container and runtime security | K3s, Falco, Kyverno, Trivy, Cosign |
| **CDP-VM** | Analytics and simulation | PostgreSQL, Mailgun, Python pipelines |
| **XDR-VM** | Detection and correlation | Elastic Stack, UEBA Model, Tines Integration |

All communication is TLS-encrypted, and access follows strict least-privilege enforcement consistent with Zero Trust principles.

---

## **6. Key Deliverables**

- **Functional MVP** integrating five Zero Trust pillars.  
- **Centralized ELK Telemetry Pipeline** with dashboards and detections.  
- **UEBA & Churn Python Models** for behavioral analytics.  
- **Six Technical Implementation Reports** (unchanged from final submission).  
- **Comprehensive Documentation** covering business, non-technical, and compliance layers.  
- **Evidence Folder** containing dashboards, screenshots, and config files.

---

## **7. Evidence & Artifacts**

| Folder | Description |
|---------|-------------|
| `/docs/technical/` | All original technical reports (PDF format). |
| `/docs/non-technical/` | Executive summary, problem statement, overview, and insights. |
| `/docs/business/` | Business case, value proposition, cost analysis, roadmap, and compliance mapping. |
| `/docs/code/` | Source code for the UEBA and Churn models. |
| `/assets/diagrams/` | Architecture diagrams — one main and five pillar-specific. |
| `/evidence/` | Screenshots, dashboards, logs, and output validation files. |

---


## **8. Roadmap Summary**

| Phase | Focus | Milestones |
|-------|--------|------------|
| **Phase 1 – MVP (Completed)** | Lab-scale validation | Integration across all five pillars |
| **Phase 2 – Optimization** | IaC automation and multi-node scaling | Terraform + Ansible deployment |
| **Phase 3 – Enterprise Integration** | SOC & compliance ecosystem | SOAR workflows and dashboard mapping |
| **Phase 4 – Intelligence Layer** | Predictive and AI-driven detections | UEBA enhancement and adaptive policy learning |

For detailed roadmap progression, refer to `/docs/business/roadmap.md`.

---

## **9. Acknowledgment**

Project Horizon was developed under the **Security Engineering & Research (SER)** as part of the *Open-Source Enterprise Zero Trust Program*.  
The project demonstrates that **cost-neutral cybersecurity maturity** can be achieved through transparency, collaboration, and engineering excellence.

---



