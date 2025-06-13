# Python Server Report

**Python Server Report** is a cross-platform utility that runs as a background service (Windows Service or systemd daemon), collects system information (IP, MAC, hostname, OS, CPU, memory, disk, users) at configurable intervals, and emails a templated report via SMTP.

---

## 📁 Repository Layout

```
.
├── config.yaml             # YAML configuration
├── requirements.txt        # Python dependencies
├── main.py                 # Scheduler & report logic
├── windows_service.py      # Windows Service wrapper
└── linux_server.service    # systemd unit file (Linux)
```

---

## ⚙️ Prerequisites

- Python 3.7+  
- pip  
- On Windows: `pywin32` installed, Administrative rights to install a Service  
- On Linux: `systemd` and `sudo`

---

## 🔧 Installation

1. **Clone repository**  
    ```bash
    git clone https://github.com/youruser/python-server-report.git
    cd python-server-report
    ```

2. **Install dependencies**  
    ```bash
    pip install -r requirements.txt
    ```

---

## 🛠️ Configuration

Edit `config.yaml` to set your schedule, SMTP server details and logging:

```yaml
schedule: "@every 30m"  # or cron: "0 8 * * *"
smtp:
  host: "smtp.example.com"
  port: 587
  username: "alert@example.com"
  password: "supersecret"
  sender:   "alert@example.com"
  recipients:
    - "admin1@example.com"
    - "admin2@example.com"
log:
  path: "server.log"
  level: "INFO"
```

- **Interval syntax**:  
  - `@every 30m` for every 30 minutes  
  - Cron-style (`M H D M W`), e.g. `0 8 * * *` at 08:00 daily

---

## ▶️ Running Manually

```bash
python main.py
```

Your reports will be logged to `server.log` and emailed per schedule. Press `Ctrl+C` to stop.

---

## ⚙️ Windows Service

1. **Install service**:  
   ```powershell
   python windows_service.py install
   ```
2. **Start service**:  
   ```powershell
   python windows_service.py start
   ```
3. **Stop & remove**:  
   ```powershell
   python windows_service.py stop
   python windows_service.py remove
   ```

Logs will appear in `server.log` (or Windows Event Viewer if configured).

---

## ⚙️ Linux systemd Unit

1. **Copy files**:  
   ```bash
   sudo mkdir -p /opt/server-report
   sudo cp main.py config.yaml /opt/server-report/
   sudo cp linux_server.service /etc/systemd/system/python-server-report.service
   ```

2. **Enable & start**:  
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable python-server-report
   sudo systemctl start python-server-report
   ```

3. **Check status & logs**:  
   ```bash
   sudo systemctl status python-server-report
   journalctl -u python-server-report -f
   ```

---

## 🐞 Troubleshooting

- **Email failures**: check SMTP credentials and network access.  
- **Permission errors**: ensure your user has rights to install services or write logs.  
- **Scheduler not firing**: validate your `schedule` syntax in `config.yaml`.  

---

## 📄 License

This project is licensed under the GPL License.  
