# service.py
import sys, os
import win32serviceutil, win32service, win32event, servicemanager

SERVICE_NAME = "PyServerReport"
SERVICE_DESC = "Periodic System Report Service"

# point to app.py directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = sys.executable
APP_SCRIPT = os.path.join(BASE_DIR, "app.py")

class PyReportService(win32serviceutil.ServiceFramework):
    _svc_name_        = SERVICE_NAME
    _svc_display_name_= SERVICE_NAME
    _svc_description_ = SERVICE_DESC

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        # launch app.py
        os.system(f'"{PYTHON_EXE}" "{APP_SCRIPT}"')
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

if __name__=='__main__':
    win32serviceutil.HandleCommandLine(PyReportService)
