# Compliance Mapping

## Overview

Project Horizon was designed with **compliance-by-design principles** to ensure that every layer of the Zero Trust framework—Identity, Data, Workload, and Analytics—supports regulatory and governance obligations.  
This document maps the project’s implemented controls and operational outcomes against globally recognized cybersecurity and data protection frameworks, including:

- **ISO/IEC 27001:2022**
- **NIST SP 800-207 (Zero Trust Architecture)**
- **GDPR (General Data Protection Regulation)**
- **PCI-DSS v4.0 (Payment Card Industry Data Security Standard)**

The objective is to illustrate how the architecture inherently aligns with compliance requirements through automation, visibility, and auditable control mechanisms.

---

## 1. ISO/IEC 27001:2022 Mapping

| ISO 27001 Control | Description | Horizon Implementation |
|--------------------|--------------|-------------------------|
| **A.5.1 Information Security Policies** | Establish and maintain information security policies. | Policies codified through Kyverno and Cloud Custodian define explicit configurations for every system component. |
| **A.6.1 Organization of Information Security** | Roles and responsibilities for information security. | RBAC and Keycloak identity federation enforce role-based access aligned to security principles. |
| **A.8.1 Asset Management** | Identification and inventory of assets. | DSPM automatically scans and inventories data repositories using NiFi and MinIO metadata pipelines. |
| **A.9.1 Access Control** | Restrict access based on least privilege. | Zero Trust enforcement via Keycloak (IAM) and Pomerium (context-aware proxy). |
| **A.12.4 Logging and Monitoring** | Capture and review security events. | Centralized telemetry ingestion via Elastic Stack with retention and integrity checks. |
| **A.14.2 Secure Development** | Control changes in software and systems. | GitOps workflows, signed containers (Cosign), and IaC validation via Checkov. |
| **A.16.1 Incident Management** | Establish processes to manage incidents. | Automated alert forwarding to dashboards and incident channels using XDR pipeline. |
| **A.18.1 Compliance with Legal and Contractual Requirements** | Ensure legal and regulatory adherence. | Custodian-driven policy enforcement ensures compliance with data residency and retention laws. |

---

## 2. NIST SP 800-207 (Zero Trust Architecture)

| NIST Principle | Description | Horizon Implementation |
|----------------|--------------|-------------------------|
| **Continuous Verification** | Access decisions based on dynamic, real-time trust evaluation. | Session-based access tokens validated via Keycloak and Pomerium with TLS inspection. |
| **Least Privilege Access** | Limit access rights to only what is required. | Role-mapped and attribute-based access control integrated into ZTNA and CNAPP layers. |
| **Microsegmentation** | Divide network resources into secure zones. | Namespace isolation and Kubernetes network policies enforce micro-perimeters. |
| **Visibility and Analytics** | Collect and analyze data from all sources. | Centralized Elastic analytics integrating telemetry from identity, workloads, and data. |
| **Automation and Orchestration** | Automate response to detected threats. | Automated policy remediation via Kyverno and Cloud Custodian. |
| **Dynamic Policy Enforcement** | Policies adapt to context and risk level. | Integration of UEBA model outputs into adaptive access logic. |

---

## 3. GDPR Compliance Alignment

| GDPR Article | Requirement | Horizon Mechanism |
|---------------|-------------|------------------|
| **Art. 5 – Principles of Data Processing** | Lawful, fair, and transparent processing. | DSPM ensures data traceability and classification; access governed through IAM policies. |
| **Art. 25 – Data Protection by Design and Default** | Security and privacy integrated into systems. | Privacy filters embedded at collection points using Presidio and NiFi processors. |
| **Art. 30 – Record of Processing Activities (ROPA)** | Maintain logs of processing operations. | Automated audit trails and immutable logs within Elastic Stack. |
| **Art. 32 – Security of Processing** | Implement security controls proportional to risk. | Encryption in transit (TLS) and at rest (MinIO SSE), coupled with runtime scanning. |
| **Art. 33 – Breach Notification** | Notify supervisory authority within 72 hours. | Real-time alert triggers and centralized monitoring dashboards support rapid incident escalation. |
| **Art. 35 – Data Protection Impact Assessments (DPIA)** | Conduct risk assessments for new processing. | Configurable scanning workflows in NiFi provide continuous sensitivity analysis. |

---

## 4. PCI-DSS v4.0 Mapping

| PCI-DSS Requirement | Control Objective | Horizon Implementation |
|---------------------|--------------------|-------------------------|
| **1.1 – Network Security Controls** | Install and maintain firewalls and segmentation. | Pomerium gateway and Kubernetes network policies enforce application-layer segmentation. |
| **3.4 – Data Protection** | Protect stored cardholder data. | AES-based encryption and access logging in MinIO ensure confidentiality. |
| **7.1 – Access Control Measures** | Restrict access to cardholder data by need-to-know. | Identity-attribute-based access through Keycloak policies. |
| **10.2 – Audit Trails** | Track and monitor access to network resources. | Full telemetry ingestion into Elastic Stack with dashboards and retention indices. |
| **11.4 – Intrusion Detection Mechanisms** | Implement IDS/IPS solutions. | Falco runtime detection and Suricata network inspection integrated into CNAPP. |
| **12.2 – Risk Assessment** | Identify and assess security risks annually. | Automated compliance and asset scanning pipelines in DSPM and CNAPP frameworks. |

---

## 5. Cross-Framework Synergies

| Function | Horizon Feature | Supported Frameworks |
|-----------|-----------------|----------------------|
| **Identity and Access Control** | Keycloak + Pomerium | ISO 27001, NIST, GDPR, PCI-DSS |
| **Logging and Monitoring** | Elastic Stack | ISO 27001, NIST, PCI-DSS |
| **Data Discovery and Privacy Enforcement** | DSPM (NiFi, Presidio, Custodian) | GDPR, ISO 27001 |
| **Runtime Protection** | Falco, Kyverno, Trivy, Cosign | NIST, PCI-DSS |
| **Incident Detection and Analytics** | XDR + UEBA | NIST, ISO 27001 |
| **Governance and Auditability** | Centralized dashboards, immutable indices | All frameworks |

---

## 6. Audit and Evidence Readiness

Horizon maintains **immutable, timestamped telemetry** across all key domains, ensuring that every compliance control is verifiable. Evidence includes:

- Configuration manifests and signed container digests.  
- Enriched audit logs stored with retention and hash integrity.  
- Real-time dashboards mapping security posture to regulatory requirements.  
- Automated reports exportable in CSV, JSON, or PDF formats for auditors.

This enables **continuous compliance**, where every operational activity is inherently auditable, measurable, and reproducible.

---

## 7. Continuous Compliance Roadmap

- **Automated Compliance Dashboards:** Integration with Elastic Canvas and Kibana Lens to map controls visually.  
- **SOAR Integration:** Future link to orchestration engines for auto-remediation and reporting to compliance officers.  
- **Policy-as-Code Enhancements:** Extending Kyverno and Custodian for adaptive risk-based compliance validation.  
- **Cross-Framework Correlation:** Unified mapping of NIST, ISO, GDPR, and SOC 2 to streamline global readiness.  
- **Annual Review and Gap Analysis:** Regular validation of control coverage and maturity scoring.

---

## Conclusion

Project Horizon not only implements robust technical controls but does so within a framework that inherently supports global compliance objectives.  
Through its modular, auditable, and automation-first design, Horizon delivers **continuous assurance**, **policy transparency**, and **evidence-driven accountability**, aligning security operations with the world’s leading compliance standards.
