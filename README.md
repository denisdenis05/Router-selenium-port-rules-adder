# Router selenium port rules adder

### Auto Port Forwarding Script made for routers without ssh/telnet access, only web config
**Tested on Huawei HG6544C (FiberHome firmware variant)**

## Overview


### PortCheck is a Python automation tool that:

- Checks if a specific port on a public hostname is open.
- If the port is closed, it runs a Selenium script to log into your router and re-add the port forwarding rule.
- Supports multiple port forwarding rules.
- Runs automatically on a schedule using systemd timers.

---

### Features

- Multiple rules: Configure multiple (Private IP, Public Port, Private Port) rules.
- Smart add: Only adds a rule if it’s missing.
- Verification: Confirms the rule exists after adding.
- Automation: Runs automatically via systemd timer.
- Virtual environment: Isolated Python environment for dependencies.

---

### Requirements

- Python 3.8+
- Firefox browser
- Geckodriver installed and in PATH
- nc (netcat) for port checking
- Linux server with systemd

---

## Installation

### Create virtual environment
```
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Configuration
```
ROUTER_URL = "http://192.168.1.1"
USERNAME = "your_router_username"
PASSWORD = "your_router_password"

# List of rules: (Private IP, Public Port, Private Port)
RULES = [
    ("192.168.1.80", "22", "22"),
    ("192.168.1.81", "8080", "80"),
]
```

### Manual run
```
source venv/bin/activate
python portcheck.py
```

