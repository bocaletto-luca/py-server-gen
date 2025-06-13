# app.py
import os, sys, time, socket, getpass, platform, logging, yaml, psutil
from email.mime.text import MIMEText
import smtplib
from apscheduler.schedulers.blocking import BlockingScheduler

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.yaml")

def load_config():
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)

def setup_logging(cfg):
    lvl = getattr(logging, cfg["log"].get("level","INFO").upper(), logging.INFO)
    logging.basicConfig(
        filename=cfg["log"]["path"], level=lvl,
        format="%(asctime)s %(levelname)s %(message)s"
    )

def gather_info():
    info = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hostname":  socket.gethostname(),
        "os":        f"{platform.system()} {platform.release()}",
        "user":      getpass.getuser(),
        "cpu":       psutil.cpu_percent(interval=1),
    }
    vm = psutil.virtual_memory()
    info["mem"] = {"total": vm.total, "used": vm.used}
    info["disk"] = {
        p.mountpoint: psutil.disk_usage(p.mountpoint)._asdict()
        for p in psutil.disk_partitions()
    }
    info["interfaces"] = []
    for iface, addrs in psutil.net_if_addrs().items():
        mac = next((a.address for a in addrs if a.family.name=="AF_LINK"), "")
        for a in addrs:
            if a.family.name in ("AF_INET","AF_INET6"):
                info["interfaces"].append({
                    "iface": iface,
                    "address": a.address,
                    "mac": mac
                })
    return info

def send_report(cfg):
    try:
        info = gather_info()
        lines = [f"{k}: {v}" for k,v in info.items() if k!="interfaces"]
        body = "\n".join(lines) + "\nInterfaces:\n"
        for i in info["interfaces"]:
            body += f"  - {i['iface']} IP={i['address']} MAC={i['mac']}\n"

        msg = MIMEText(body)
        msg["Subject"] = f"[Report] {info['hostname']} @ {info['timestamp']}"
        msg["From"]    = cfg["smtp"]["sender"]
        msg["To"]      = ", ".join(cfg["smtp"]["recipients"])

        with smtplib.SMTP(cfg["smtp"]["host"], cfg["smtp"]["port"], timeout=30) as s:
            s.starttls()
            s.login(cfg["smtp"]["username"], cfg["smtp"]["password"])
            s.send_message(msg)

        logging.info("Report sent")
    except Exception:
        logging.exception("Failed to send report")

def main():
    cfg = load_config()
    setup_logging(cfg)
    sched = BlockingScheduler()
    spec = cfg["schedule"]
    if spec.startswith("@every"):
        n, unit = int(spec.split()[1][:-1]), spec.split()[1][-1]
        secs = n*(60 if unit=="m" else 1)
        sched.add_job(lambda: send_report(cfg), "interval", seconds=secs)
    else:
        m,h,dom,mon,dow = spec.split()
        sched.add_job(lambda: send_report(cfg), "cron",
                      minute=m, hour=h, day=dom, month=mon, day_of_week=dow)
    logging.info(f"Scheduler starts ({spec})")
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__=="__main__":
    main()
