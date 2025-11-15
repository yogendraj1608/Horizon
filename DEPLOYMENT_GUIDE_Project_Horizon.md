# Project Horizon – Unified Zero Trust Security & Operations Platform

## Architecture 
<img width="2550" height="2274" alt="MAIN - Horizon" src="https://github.com/user-attachments/assets/986351be-8f66-443a-9501-731e30be4dc1" />


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

---


# Addendum — Full Integration Parity

## CNAPP: Kyverno Policies and Cosign Signing

```bash
curl -sSL https://raw.githubusercontent.com/sigstore/cosign/main/install.sh | sh
cosign generate-key-pair
cosign sign --key cosign.key docker.io/library/nginx:1.25
cosign verify --key cosign.pub docker.io/library/nginx:1.25
```

Create `kyverno-policy-verify-signed.yaml`:
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-signed-images
spec:
  validationFailureAction: enforce
  background: true
  rules:
  - name: require-signed
    match:
      any:
      - resources:
          kinds: ["Pod"]
    verifyImages:
    - imageReferences: ["*"]
      attestors:
      - entries:
        - keys:
            publicKeys: |
              -----BEGIN PUBLIC KEY-----
              <paste cosign.pub>
              -----END PUBLIC KEY-----
```

Deploy Kyverno and apply the policy:
```bash
helm repo add kyverno https://kyverno.github.io/kyverno/
helm install kyverno kyverno/kyverno -n kyverno --create-namespace
kubectl apply -f kyverno-policy-verify-signed.yaml
```

## Checkov (IaC Static Analysis)

```bash
pip install checkov
checkov -d ./manifests
checkov -d ./infra/terraform
```

## Mailgun Alert Integration

```bash
export MAILGUN_DOMAIN="mg.example.com"
export MAILGUN_KEY="key-xxxxxxxxxxxxxxxx"

cat > /usr/local/bin/horizon-mailgun.py <<'PY'
import os, sys, requests, json
d=os.getenv("MAILGUN_DOMAIN"); k=os.getenv("MAILGUN_KEY")
evt=json.loads(sys.stdin.read())
sub=f"[HORIZON] {evt.get('rule','Alert')} severity={evt.get('severity','')}"
txt=json.dumps(evt, indent=2)
requests.post(f"https://api.mailgun.net/v3/{d}/messages",
    auth=("api", k),
    data={"from":"horizon@"+d,"to":["soc@example.com"],"subject":sub,"text":txt})
PY
chmod +x /usr/local/bin/horizon-mailgun.py
```

Local Flask webhook forwarder:

```bash
pip install flask requests
python3 - <<'PY'
from flask import Flask, request
import subprocess, json
app=Flask(__name__)
@app.post("/mailgun")
def mg():
    evt=request.get_json(force=True)
    subprocess.run(["/usr/local/bin/horizon-mailgun.py"],input=json.dumps(evt).encode())
    return ("ok",200)
app.run(host="0.0.0.0", port=8080)
PY
```

## SOAR (Tines Integration)

In Kibana → **Stack Management → Connectors**, create a Webhook connector pointing to the Tines ingest endpoint.  
Attach it to detection rules using:

```sql
FROM logs-* | WHERE event.kind == "alert" OR rule.name IS NOT NULL
```

Sample body template:
```json
{
  "source": "{{context.index}}",
  "rule": "{{context.rule.name}}",
  "severity": "{{context.alerts.0._source.event.severity}}",
  "doc": "{{context.alerts.0._id}}"
}
```

## UEBA (Behavioral Analytics)

```bash
pip install pandas scikit-learn elasticsearch jq
python3 - <<'PY'
from elasticsearch import Elasticsearch
from sklearn.ensemble import IsolationForest
import pandas as pd
es=Elasticsearch("http://localhost:9200")
hits=es.search(index="auth-*", size=5000, query={"match_all":{}})["hits"]["hits"]
df=pd.json_normalize([h["_source"] for h in hits])
features=df[["source.ip","event.outcome"]].assign(
    fail=(df["event.outcome"]=="failure").astype(int)
).fillna(0)
model=IsolationForest(contamination=0.03, random_state=42).fit(features)
df["_score"]=model.decision_function(features)
df[["_score","source.ip","user.name"]].to_json("/tmp/ueba_scores.json", orient="records")
PY
jq -c '.[]' /tmp/ueba_scores.json | while read r; do
  curl -s -XPOST localhost:9200/ueba/_doc -H 'Content-Type: application/json' -d "$r" >/dev/null
done
```

## DSPM: NiFi → Presidio → Custodian Flow

### Presidio API

```bash
pip install presidio-analyzer presidio-anonymizer flask
python3 - <<'PY'
from presidio_analyzer import AnalyzerEngine
from flask import Flask, request, jsonify
app=Flask(__name__); ae=AnalyzerEngine()
@app.post("/analyze")
def analyze():
    text=request.get_json()["text"]
    res=[r.to_dict() for r in ae.analyze(text=text, language="en")]
    return jsonify({"pii_detected": bool(res), "entities": res})
app.run("0.0.0.0",5005)
PY
```

### Custodian Policy for MinIO

```yaml
policies:
- name: ds-redact-pii
  resource: s3
  filters:
    - type: data
      expr: "pii_detected == true"
  actions:
    - type: notify
      to: [ "security@example.com" ]
      transport:
        type: sqs
        queue: https://sqs/...
```

## pfSense + Suricata → ELK Integration

- pfSense forwards mirrored/ingress traffic to Suricata monitoring interface (SPAN/TAP).  
- Suricata `eve.json` logs are shipped to ELK via Filebeat → Logstash → Elasticsearch.  
- Kibana dashboards include index patterns `filebeat-*`, `suricata-*`, `falco-*`, `cdp-*` for unified visibility.

## Repository Reference Map

- `docs/technical/` → Detailed pillar PDFs and technical documents.  
- `assets/diagrams/` → Architecture and component diagrams.  
- `evidence/` → Screenshots, validation proofs, and test results.

---


## 7️⃣ POC

## 1. CDP


<div align="left">
 <img width="940" height="195" alt="image" src="https://github.com/user-attachments/assets/f1de2546-c55b-4438-a08d-2544e6554e48" />
<p><strong>Database Evidence</strong></p>
</div>

<br>

<div align="left">
 <img width="940" height="389" alt="image" src="https://github.com/user-attachments/assets/408c6412-be1e-4603-a823-e46169774a81" />
 <p><strong>Scoring & Alert Logs</strong></p>
</div>

<br>

<div align="left">
<img width="944" height="381" alt="image" src="https://github.com/user-attachments/assets/7ca86c3a-d676-4afe-9b94-af483da03a0d" />
 <p>Confirms end-to-end mail delivery via Mailgun integration.</p>
</div>

<br>

<div align="left">
<img width="944" height="451" alt="image" src="https://github.com/user-attachments/assets/1da17a0c-a041-472e-a42f-60a757448e46" />
 <p>Verified records show fields like user_id, segment, status, campaign_id.</p>
</div>

<br>

<div align="left">
<img width="944" height="465" alt="image" src="https://github.com/user-attachments/assets/c187c3da-980d-4e0a-9668-61d7fb9e4f24" />
 <p>ELK dashboard visualizing email campaign logs and activity distribution.</p>
</div>


## 2. CNAPP
    
<div align="left">
<img width="940" height="466" alt="image" src="https://github.com/user-attachments/assets/5591ecca-c258-4179-a8b8-e102973def00" />
 <p>Misconfiguration alerts were visible in checkov-* index patterns and dashboards in Kibana.</p>
</div>

<br>

<div align="left">
<img width="940" height="432" alt="image" src="https://github.com/user-attachments/assets/cb1a3ade-407a-4f50-9c94-4d4ef47d4153" />
 <p>Container images were signed with Cosign before pushing to the private registry.</p>
</div>

<br>

<div align="left">
<img width="939" height="578" alt="image" src="https://github.com/user-attachments/assets/74d9e7f0-de64-444d-bb3f-5eaf1d98d461" />
 <p>Kyverno policies require-image-signature and verify-signed-images enforced signature verification during admission.</p>
</div>

<br>

<div align="left">
<img width="944" height="479" alt="image" src="https://github.com/user-attachments/assets/d3e08e29-fc69-44dc-acd0-1c621c72eb04" />
<p>Kyverno admission logs were ingested into Elasticsearch and visualized through kyverno-* dashboards.</p>
</div>

<br>

<div align="left">
<img width="937" height="674" alt="image" src="https://github.com/user-attachments/assets/500a4086-af7d-42ae-b801-7fc86ee4aeef" />
 <p>Trivy was used to scan container images in the private registry.</p>
</div>

 <br>
 
<div align="left">
<img width="944" height="414" alt="image" src="https://github.com/user-attachments/assets/2d36ed20-8a0b-4b51-a123-9692804f8c89" />
 <p>Vulnerability reports appeared in trivy-* index patterns and Kibana dashboards.</p>
</div>

<br>

<div align="left">
<img width="939" height="427" alt="image" src="https://github.com/user-attachments/assets/5b5daffb-470d-4d1e-9bf4-80696ae86bd7" />
 <p>Falco generated alerts for anomalous runtime activities, including terminal access to containers and API server contact.</p>
</div>

<br>

<div align="left">
<img width="944" height="477" alt="image" src="https://github.com/user-attachments/assets/debc14c8-946f-4471-9732-182745d31368" />
 <p>Alerts appeared in the falco-* indices in Elasticsearch.</p>
</div>

<br>

<div align="left">
<img width="944" height="460" alt="image" src="https://github.com/user-attachments/assets/dc38a42b-2b0a-4c40-9ea9-786377f3d7f5" />
 <p>Elastic Agent successfully collected logs from Checkov, Kyverno, Trivy, and Falco.</p>
</div>

<br>

<div align="left">
<img width="944" height="480" alt="image" src="https://github.com/user-attachments/assets/50c12203-37b9-4159-a202-db6b4c92b038" />
 <p>All components’ telemetry was flowing correctly into Elasticsearch.</p>
</div>

<br>

<div align="left">
<img width="944" height="458" alt="image" src="https://github.com/user-attachments/assets/dc0dde40-af69-443c-a43e-36f4d72d747d" />
</p>
<div align="left">
<img width="940" height="453" alt="image" src="https://github.com/user-attachments/assets/2a078d10-27ae-44a4-b331-e8102222ee5a" />
 <p>Kibana dashboards presented correlated views across IaC misconfigurations, vulnerabilities, policy violations, and runtime detections.</p>
</div>


## 3. DSPM

<div align="left">
<img width="944" height="443" alt="image" src="https://github.com/user-attachments/assets/6048884b-4b1c-4b02-8e8b-1cd4cbf085dc" />
  <p>Confirms that datasets containing PII/PCI are correctly ingested into the controlled object storage environment.</p>
</div>

<br>

<div align="left">
<img width="944" height="461" alt="image" src="https://github.com/user-attachments/assets/77464eef-ddec-441e-a536-2688dde6967e" />
  <p>Demonstrates dynamic data flow tracking and lineage visibility.</p>
</div>

<br>

<div align="left">
<img width="945" height="213" alt="image" src="https://github.com/user-attachments/assets/09b1070d-3dfa-4751-82b4-bd2e9c3e4f52" />
 <p>Confirms sensitive records are persisted into a relational database for compliance monitoring.</p>
</div>

<br>

<div align="left">
<img width="944" height="216" alt="image" src="https://github.com/user-attachments/assets/3175bbfc-6f8b-44a6-a120-28443460a2e4" />
  <p>Confirms entity-level discovery of PII/PCI data with high accuracy.</p>
</div>

<br>

<div align="left">
<img width="938" height="252" alt="image" src="https://github.com/user-attachments/assets/255191a6-4deb-4ee6-916d-163854647f75" />
 <p>Confirms automated enforcement of storage policies against misconfiguration.</p>
</div>

<br>

<div align="left">
<img width="944" height="422" alt="image" src="https://github.com/user-attachments/assets/ea469471-5341-4d69-b24e-e73b02678e14" />
  <p>Confirms that custom log pipeline integrates DSPM components into centralized monitoring.</p>
</div>


## 4. XDR

<div align="left">
  <img width="944" height="482" alt="image" src="https://github.com/user-attachments/assets/c7d63aa0-edb2-49fa-b22d-413889d79c92" />
  <p>Successful ingestion was confirmed through sample login events from contractor1@aether.local and corresponding Kibana searches</p>
</div>

<br>

<div align="left">
  <img width="944" height="478" alt="image" src="https://github.com/user-attachments/assets/6bdc4c5d-41bc-4681-a908-ffeb623181ae" />
  <p>EVE JSON alerts indexed under logs-suricata-*.</p>
</div>

<br>

<div align="left">
  <img width="944" height="390" alt="image" src="https://github.com/user-attachments/assets/34cc0f48-63ff-4f4e-90c9-b9af56941d8a" />
  <p>Detection rules.</p>
</div>

<br>

<div align="left">
  <img width="944" height="490" alt="image" src="https://github.com/user-attachments/assets/4a558f22-7d3f-417e-a50e-390bd48e5d01" />
  <p>Several normal login sessions were generated during standard work hours for multiple users.</p>
</div>

<br>

<div align="left">
  <img width="944" height="490" alt="image" src="https://github.com/user-attachments/assets/dfb47bc1-5484-480f-a407-ec72b2a6361b" />
  <p>Anomaly Injection</p>
</div>

<br>

<div align="left">
  <img width="940" height="480" alt="image" src="https://github.com/user-attachments/assets/e22c86b4-decd-43d0-87d5-588adf23af1a" />
  <p>Streamlit dashboard screenshots showing anomaly severity distributions and user drill-down views.</p>
</div>

<br>

<div align="left">
  <img width="944" height="464" alt="image" src="https://github.com/user-attachments/assets/a07f256d-5376-4733-bcad-ea5650266ec0" />
  <p>Email alert samples received for critical anomalies with full context (incident ID, IP reputation, analyst recommendations).</p>
</div>

<br>

<div align="left">
  <img width="944" height="459" alt="image" src="https://github.com/user-attachments/assets/81129811-601c-4db8-82db-46894c8abf8a" />
  <p>DSPM Dashboard: Visualized DLP alerts and Custodian remediation actions.</p>
</div>

<br>

<div align="left">
  <img width="944" height="947" alt="image" src="https://github.com/user-attachments/assets/eefcd1b9-60b7-4aba-9a40-ba545ed25f30" />
  <p>CDP Dashboard: Monitoring pipeline stages, campaigns, and outcomes.</p>
</div>

<br>

<div align="left">
  <img width="944" height="486" alt="image" src="https://github.com/user-attachments/assets/b9d306af-9a7b-4786-b180-5b9e5c3c0259" />
  <p>Network Dashboard: IDS alert categories and frequency.</p>
</div>

<br>

<div align="left">
  <img width="944" height="478" alt="image" src="https://github.com/user-attachments/assets/5b125e11-d755-4f1d-8cde-eac2b92d8ffd" />
  <p>CNAPP Dashboard: Misconfiguration trends and Kubernetes policy violation heatmaps.</p>
</div>

<br>

<div align="left">
  <img width="944" height="480" alt="image" src="https://github.com/user-attachments/assets/57382e61-7713-4c89-a727-4cd577f2b2f1" />
  <p>All dashboards were tested for filter responsiveness and real-time updates.</p>
</div>

<br>

<div align="left">
  <img width="944" height="485" alt="image" src="https://github.com/user-attachments/assets/856e6855-a322-4c7b-8b6d-d91bbb1616b8" />
  <p>Dashboards consistently loaded in <2 seconds at 95th percentile and maintained ≥90% field coverage.</p>
</div>


## 5. ZNTA

<div align="left">
  <img width="946" height="309" alt="image" src="https://github.com/user-attachments/assets/fba43ff8-3d3e-4a9a-bfa6-ceb27a032da3" />
  <p>Confirmed that Pomerium is running as a systemd service with correct binary path (/usr/sbin/pomerium) and valid configuration at /home/identity/config.yaml.</p>
</div>

<br>

<div align="left">
  <img width="940" height="431" alt="image" src="https://github.com/user-attachments/assets/100ab773-9fb4-4687-99a3-05e07c01c151" />
  <p>Initial Access</p>
</div>

<br>

<div align="left">
  <img width="940" height="455" alt="image" src="https://github.com/user-attachments/assets/258b8c0e-988b-4d94-bfa8-f57888085586" />
  <p>Identity Provider Redirection</p>
</div>

<br>

<div align="left">
  <img width="940" height="532" alt="image" src="https://github.com/user-attachments/assets/a4545dd9-c2b7-4496-885f-8220363cacc4" />
  <p>User Authentication</p>
</div>

<br>

<div align="left">
  <img width="939" height="416" alt="image" src="https://github.com/user-attachments/assets/db16ad07-a9a0-4b9f-b9c0-6f190dc38ac1" />
  <p>Pomerium Logs</p>
</div>

<br>

<div align="left">
  <img width="940" height="185" alt="image" src="https://github.com/user-attachments/assets/bfcd2b77-2503-4f3d-be5a-1bb8548dc028" />
  <p>Keycloak Logs</p>
</div>

<br>

<div align="left">
  <img width="944" height="482" alt="image" src="https://github.com/user-attachments/assets/e08e1b5b-3df2-4d12-99a7-e1d9d39d9043" />
  <p>Pomerium Sign-In Events</p>
</div>

<br>

<div align="left">
  <img width="944" height="458" alt="image" src="https://github.com/user-attachments/assets/925a33d3-2ba6-40e8-b3ae-c4c6cccdd566" />
  <p>Visualize login trends, source IPs, users, and application access patterns.</p>
</div>

<br>

<div align="left">
  <img width="940" height="499" alt="image" src="https://github.com/user-attachments/assets/bfd3e555-2c76-42fc-995c-7741a9bb1214" />
  <p>pfSense with Suricata IDS/IPS was deployed on the monitored virtual network.</p>
</div>

<br>

<div align="left">
  <img width="944" height="477" alt="image" src="https://github.com/user-attachments/assets/19000afb-7f66-4f47-910b-bc9b6d117c05" />
  <p>Validated visibility of HTTPS handshakes and allowed sessions through VNet inspection.</p>
</div>

---
