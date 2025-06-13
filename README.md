# Python Persistent Server Reporter
#### Author: Bocaletto Luca

**Python Persistent Server Reporter** è un’applicazione cross-platform che:

1. Raccoglie metriche di sistema (IP, MAC, hostname, OS, CPU, memoria, disco, utenti)  
2. Invia report via SMTP a intervalli configurabili  
3. Gira in background come **Windows Service** o **systemd daemon**  
4. Si riavvia automaticamente in caso di crash o kill  
5. Auto-parte all’avvio del sistema  

---

## 📋 Prerequisiti

- Python 3.7+  
- pip (o venv)  
- Su **Windows**: privilegi di amministratore per installare il servizio  
- Su **Linux**: `systemd` e permessi `sudo`  

---

## 📥 Installazione

```bash
git clone https://github.com/youruser/python-reporter.git
cd python-reporter
pip install -r requirements.txt
```

---

## ⚙️ Configurazione

Modifica `config.yaml` secondo le tue esigenze:

```yaml
schedule: "@every 30m"      # oppure cron "0 8 * * *"
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

---

## ▶️ Esecuzione Manuale

```bash
python main.py
```

- Il processo rimane in foreground  
- CTRL+C per terminare

---

## ⚙️ Installazione come Servizio

### Windows

1. Installa il servizio:
   ```powershell
   python windows_service.py install
   ```
2. Configura recovery policy:
   ```powershell
   sc.exe failure PyServerReport reset= 0 actions= restart/5000
   ```
3. Avvia:
   ```powershell
   python windows_service.py start
   ```
4. Stop & rimozione:
   ```powershell
   python windows_service.py stop
   python windows_service.py remove
   ```

### Linux (systemd)

1. Copia file:
   ```bash
   sudo mkdir -p /opt/server-report
   sudo cp main.py config.yaml /opt/server-report/
   sudo cp linux_server.service /etc/systemd/system/python-server-report.service
   ```
2. Abilita & avvia:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable python-server-report
   sudo systemctl start python-server-report
   ```
3. Status & log:
   ```bash
   sudo systemctl status python-server-report
   journalctl -u python-server-report -f
   ```

---

## 📦 Packaging

### PyInstaller (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile app.py service.py
# quindi:
dist/service.exe install
```

### Docker

1. Costruisci immagine:
   ```bash
   docker build -t py-server-reporter .
   ```
2. Esegui:
   ```bash
   docker run -d \
     -v $(pwd)/config.yaml:/app/config.yaml:ro \
     --name py-server-report \
     py-server-reporter
   ```

---

## 🐞 Troubleshooting

- **Email failures**: controlla credenziali e port forwarding SMTP  
- **Svc non parte**: verifica che `service.py` punti al corretto interprete Python  
- **systemd non parte**: usa `journalctl -xe` per debug  

---

## 🤝 Contribuire

1. Fork del progetto  
2. Branch feature: `git checkout -b feat/my-feature`  
3. Commit e PR  

---

## 📄 Licenza

GPL License – vedi [LICENSE](LICENSE)  

---

**Autore:** Bocaletto Luca (@bocaletto-luca)  
