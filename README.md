# AWS FinOps Automation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AWS](https://img.shields.io/badge/AWS-EventBridge%20%7C%20Lambda-orange.svg)](https://aws.amazon.com/)
[![Security](https://img.shields.io/badge/security-resource--hygiene-red.svg)](https://github.com/ojackson08/aws-finops-automation)
[![Maintained by Merkaba AI Risk](https://img.shields.io/badge/maintained%20by-Merkaba%20AI%20Risk-blueviolet)](https://merkabacreatives.org/ai-risk)

**Automated resource hygiene and cost optimization for AWS environments.**

---

## Overview

An event-driven automation tool that identifies and remediates wasted cloud spend by finding and deleting unattached EBS volumes and idle EC2 instances. 

While primarily a FinOps tool, this project serves a critical security function: orphaned resources are often unpatched, unmonitored, and represent "shadow IT" attack surfaces. Automatically removing them reduces both cost and security risk.

---

## Architecture

```
Amazon EventBridge (Scheduled Rule)
    │
    ▼
AWS Lambda (FinOps Engine)
    │
    ├── Scan EC2 API for orphaned EBS volumes
    ├── Publish alert → Amazon SNS
    └── Delete orphaned resources
```

---

## Security Properties

| Property | Implementation |
|---|---|
| **Attack Surface Reduction** | Automatically removes unmonitored "shadow" resources |
| **Audit Logging** | All deletion actions are logged via CloudTrail |
| **Human in the Loop** | SNS alerts sent before destructive actions |

---

## Integration with Merkaba Security Stack

- [`aws-security-compliance-automation`](https://github.com/ojackson08/aws-security-compliance-automation) — Complements FinOps with security-focused remediation
- [`agentledger`](https://github.com/ojackson08/agentledger) — The AI agent equivalent of FinOps tracking

---

## License

MIT License — see [LICENSE](./LICENSE) for details.

---

## Contact

**Merkaba AI Risk Management**
security@merkabacreatives.org
https://merkabacreatives.org/ai-risk
