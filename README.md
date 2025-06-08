# traffic-monitoring-app

An application to monitor and control network traffic flows through a control panel. It classifies internet flows using a pre-trained neural network, indexes flow metadata in OpenSearch (with OpenSearch Dashboards for visualization), and dynamically generates blocking rules for IPs exhibiting malicious behavior.

---

## Features

- Classify network flows using a trained neural network.  
- Index flow data in OpenSearch.  
- Visualize traffic metrics in OpenSearch Dashboards.  
- Automatically generate and apply blocking rules for malicious IP addresses.  
- Generate and apply blocking rules for malicious IP addresses from control panel.  
- Additional functionality to be added as development continues.

---

## Technology Stack

- **Backend (planned)**: Python (exact framework and dependencies to be finalized)  
- **Model Inference**: Pre-trained neural network (format and runtime TBD)  
- **Search & Storage**: OpenSearch  
- **Visualization**: OpenSearch Dashboards  
- **Firewall Management**: iptables or nftables (implementation details TBD)

---

## Getting Started

1. **Clone the repository**  
   ```bash
   git clone https://github.com/danim55/traffic-monitoring-app.git
   cd traffic-monitoring-app
