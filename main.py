# main.py
import os, sys, socket, getpass, platform, logging, time, yaml, psutil
from email.mime.text import MIMEText
import smtplib
from apscheduler.schedulers.background import BackgroundScheduler

# --- load config ---
with open(os.path.join(os.path.dirname(__file__), "config.yaml")) as f:
    cfg = yaml.safe_load(f)

# --- setup logging ---
lvl = getattr(logging, cfg['log'].get('level','INFO').upper(), logging.INFO)
logging.basicConfig(
    filename=cfg['log']['path'], level=lvl,
    format="%(asctime)s %(levelname)s %(message)s"
)

# --- gather system info ---
def gather_info():
    info = {}
    info['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
    info['hostname']  = socket.gethostname()
    info['os']        = f"{platform.system()} {platform.release()}"
    info['user']      = getpass.getuser()
    # Interfaces
    info['interfaces'] = []
    for iface, addrs in psutil.net_if_addrs().items():
        mac = next((a.address for a in addrs if a.family.name=='AF_LINK'), "")
        for a in addrs:
            if a.family.name in ('AF_INET','AF_INET6'):
                info['interfaces'].append({
                    'iface': iface,
                    'address': a.address,
                    'mac': mac
                })
    info['cpu_percent'] = psutil.cpu_percent()
    vm = psutil.virtual_memory()
    info['mem'] = {'total': vm.total, 'used': vm.used}
    info['disk'] = {
        p.mountpoint: psutil.disk_usage(p.mountpoint)._asdict()
        for p in psutil.disk_partitions()
    }
    return info

# --- format & send email ---
def send_report():
    try:
        info = gather_info()
        body = "\n".join(f"{k}: {v}" for k,v in info.items() if k!='interfaces')
        body += "\nInterfaces:\n"
        for i in info['interfaces']:
            body += f"  - {i['iface']} IP={i['address']} MAC={i['mac']}\n"

        msg = MIMEText(body)
        msg['Subject'] = f"[ServerReport] {info['hostname']} @ {info['timestamp']}"
        msg['From']    = cfg['smtp']['sender']
        msg['To']      = ", ".join(cfg['smtp']['recipients'])

        with smtplib.SMTP(cfg['smtp']['host'], cfg['smtp']['port'], timeout=30) as server:
            server.starttls()
            server.login(cfg['smtp']['username'], cfg['smtp']['password'])
            server.send_message(msg)

        logging.info("Report sent successfully")
    except Exception:
        logging.exception("Failed to send report")

# --- schedule job ---
def start_scheduler():
    sched = BackgroundScheduler()
    spec = cfg['schedule']
    if spec.startswith("@every"):
        # e.g. "@every 30m"
        n, unit = int(spec.split()[1][:-1]), spec.split()[1][-1]
        secs = n * (60 if unit=='m' else 1)
        sched.add_job(send_report, 'interval', seconds=secs, next_run_time=time.time()+5)
    else:
        # cron expression "M H D M W"
        mins, hrs, dom, mon, dow = spec.split()
        sched.add_job(send_report, 'cron',
                      minute=mins, hour=hrs, day=dom, month=mon, day_of_week=dow)
    sched.start()
    logging.info(f"Scheduler started with: {spec}")
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()

if __name__ == "__main__":
    logging.info("Server starting")
    start_scheduler()
