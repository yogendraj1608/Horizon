# Project Horizon – Unified Zero Trust Security & Operations Platform

![Architecture](ad3836aa-0c73-4845-9a05-3289a58f1fce.png)

---

## Overview

**Project Horizon** is a next-generation **AI-driven Zero Trust Security & Operations Platform**, built entirely with **open-source and free-tier tools**.  
It integrates identity, data, network, workload, and detection layers into one cohesive architecture, demonstrating how enterprises can achieve **Zero Trust enforcement**, **data visibility**, **SOC modernization**, and **compliance** without licensing overheads.

### Solution Pillars
| Pillar | Purpose | Core Tools |
|--------|----------|------------|
| **ZTNA & SASE** | Identity-aware secure access and network inspection | Keycloak, Pomerium, Suricata, pfSense |
| **CDP** | Behavioral telemetry and churn analytics | PostgreSQL, Python, Mailgun, ELK |
| **DSPM** | Data discovery, classification, and policy enforcement | MinIO, Apache NiFi, Presidio, Cloud Custodian, ELK |
| **CNAPP** | Container vulnerability & runtime protection | K3s, Trivy, Falco, Kyverno, Cosign |
| **XDR & Insider Risk** | Centralized telemetry and detection engineering | ELK Stack, UEBA modules, ES|QL rules |

---

## 1️⃣ Environment Topology

| VM | Role | OS | Tools Installed |
|----|------|----|----------------|
| **VM-1: Identity Gateway** | Keycloak (IdP), Pomerium (proxy) | Ubuntu 20.04 LTS | Keycloak 21.x, Pomerium, Nginx, Certbot |
| **VM-2: Network Sensor** | Suricata IDS + pfSense routing | Ubuntu 20.04 / pfSense CE | Suricata 6.x, Filebeat |
| **VM-3: Data Platform** | DSPM components | Ubuntu 22.04 | MinIO, Apache NiFi, Presidio, Cloud Custodian |
| **VM-4: Workload Security** | CNAPP lab | Ubuntu 22.04 | K3s, Trivy, Falco, Falcosidekick |
| **VM-5: Analytics & SOC** | ELK Stack + UEBA | Ubuntu 22.04 | Elasticsearch 8.x, Logstash, Kibana |

Each VM uses self-signed TLS certificates (`/etc/ssl/horizon/*.crt`) and internal DNS entries (e.g., `keycloak.horizon.local`) for secure communication.

---

## 2️⃣ Installation & Configuration

### A. Identity & Access (ZTNA & SASE)

**Install Keycloak**
```bash
sudo apt update && sudo apt install default-jre -y
wget https://github.com/keycloak/keycloak/releases/download/21.1.1/keycloak-21.1.1.tar.gz
tar -xzf keycloak-21.1.1.tar.gz && cd keycloak-21.1.1/bin
./kc.sh start-dev --http-port 8080
```

- Create Realm: `Horizon`
- Add Roles: `admin`, `analyst`, `developer`
- Add Users and assign roles  
- Enable HTTPS → `conf/keycloak.conf` → `https-port=8443`

**Install Pomerium**
```bash
curl -L https://github.com/pomerium/pomerium/releases/latest/download/pomerium-linux-amd64 -o /usr/local/bin/pomerium
chmod +x /usr/local/bin/pomerium
```
Edit `/etc/pomerium/config.yaml`:
```yaml
authenticate_service_url: https://keycloak.horizon.local
idp_provider: "oidc"
idp_client_id: "horizon-client"
idp_client_secret: "<secret>"
routes:
  - from: https://dashboard.horizon.local
    to: http://10.0.0.3:5601
    policy:
      - allow:
          or:
            - email: admin@horizon.local
```
Start:
```bash
sudo systemctl enable pomerium && sudo systemctl start pomerium
```

**Suricata (IDS)**
```bash
sudo apt install suricata -y
sudo suricata-update
sudo systemctl enable suricata && sudo systemctl start suricata
```
Enable JSON output in `/etc/suricata/suricata.yaml`:
```yaml
outputs:
  - eve-log:
      enabled: yes
      types:
        - alert
        - dns
        - tls
        - http
```
Ship logs via Filebeat → Logstash.

---

### B. Customer Data Platform (CDP)

```bash
sudo apt install postgresql postgresql-contrib python3-pip -y
pip install psycopg2-binary requests elasticsearch
```

**Database Setup**
```sql
CREATE DATABASE cdp;
CREATE TABLE users(id SERIAL PRIMARY KEY, email TEXT, sessions INT, churn_score FLOAT);
```

**Python Pipeline**
```python
import psycopg2, requests, json, random, time
while True:
    score = random.random()
    event = {"user":"user1","churn_score":score,"timestamp":time.time()}
    requests.post("http://elk.local:9200/cdp/_doc", json=event)
    time.sleep(10)
```

---

### C. Data Security Posture Management (DSPM)

```bash
sudo apt install openjdk-11-jre -y
wget https://downloads.apache.org/nifi/1.25.0/nifi-1.25.0-bin.zip
unzip nifi-1.25.0-bin.zip && ./nifi-1.25.0/bin/nifi.sh start
```

**MinIO**
```bash
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio && ./minio server /data
```

**Presidio & Custodian**
```bash
pip install presidio-analyzer presidio-anonymizer cloud-custodian
```
Example Custodian policy (`policy.yml`)
```yaml
policies:
  - name: redact-pii
    resource: s3
    filters:
      - type: data
        expr: "pii_detected == true"
    actions:
      - type: redact
      - type: notify
```

---

### D. CNAPP (Workload Protection)

```bash
curl -sfL https://get.k3s.io | sh -
sudo systemctl enable k3s
```

**Trivy Scanner**
```bash
sudo apt install trivy -y
trivy image nginx:latest --format json --output /var/log/trivy.json
```

**Falco Runtime**
```bash
curl -s https://falco.org/repo/falcosecurity.gpg | sudo apt-key add -
sudo apt install falco -y
sudo systemctl enable falco && sudo systemctl start falco
```

**Falcosidekick**
```bash
docker run -d -p 2801:2801 -e FALCOSIDEKICK_ELASTICSEARCH_HOSTPORT=elk.local:9200 falcosecurity/falcosidekick
```

---

### E. XDR & Insider Risk (Detection Fabric)

```bash
sudo apt install elasticsearch logstash kibana -y
```
**Logstash Pipeline Example**
```bash
input { beats { port => 5044 } }
filter {
  json { source => "message" }
}
output {
  elasticsearch { hosts => ["localhost:9200"] index => "%{[@metadata][type]}-%{+YYYY.MM.dd}" }
}
```

**Detection Rule Example (ES|QL)**
```sql
FROM auth-*, net-* 
WHERE event.action == "login_failed"
GROUP BY src_ip
HAVING count() > 5
```

---

## 3️⃣ Integration Workflow

1. **User Authentication:** Keycloak authenticates → Pomerium applies route-based access.  
2. **Network Inspection:** Suricata monitors ingress traffic, forwards alerts to ELK.  
3. **Data Flow & Classification:** NiFi routes data → Presidio classifies PII → Custodian applies policy.  
4. **Workload Monitoring:** Trivy scans images, Falco detects runtime events.  
5. **Telemetry Correlation:** All logs → Logstash → Elasticsearch; Kibana dashboards show identity + network + data + runtime views.  
6. **Detection & Alerting:** ES|QL rules and UEBA detect multi-stage threats and insider anomalies.

---

## 4️⃣ Dashboards & Validation

| Dashboard | Description |
|------------|-------------|
| **Attack Timeline** | Chronological view of cross-pillar events |
| **Policy Violations** | DSPM rule breaches by type |
| **Container Threats** | Falco runtime alerts and Trivy vulnerabilities |
| **Authentication Insights** | Keycloak login success/failure rates |
| **Insider Risk View** | UEBA anomaly scores from CDP telemetry |

---

## 5️⃣ Scaling Roadmap (Next Phases)

| Phase | Focus | Key Additions |
|--------|--------|---------------|
| **Phase 1** | Federation & PKI | Integrate Azure AD/Okta, MFA, ACME certs |
| **Phase 2** | Scaling & Compliance | Clustered ELK, HA Keycloak, GDPR dashboards |
| **Phase 3** | Automation & SOAR | Cortex/Tines playbooks, threat intel feeds, automated response |

---

## 6️⃣ Expected Outcome

- End-to-end Zero Trust enforcement  
- Centralized telemetry and XDR visibility  
- Real-time DSPM and runtime detection  
- Scalable blueprint for enterprise SOC modernization  
- 100 % open-source stack validated with cross-layer integration 
