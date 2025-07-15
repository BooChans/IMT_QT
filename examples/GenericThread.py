from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QMetaObject, Qt, Q_ARG
from ifmta.ifta import IftaImproved

class GenericThread(QThread):

    progress_changed = pyqtSignal(int)
    finished_with_result = pyqtSignal(object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

        def progress_callback(percent):
            QMetaObject.invokeMethod(self, "_emit_progress", Qt.QueuedConnection, Q_ARG(int, int(percent)))

        self.kwargs["callback"] = progress_callback
        self.result = None

    @pyqtSlot(int)
    def _emit_progress(self, val):
        self.progress_changed.emit(val)

    def run(self):
        self.result = self.func(*self.args, **self.kwargs)
        self.finished_with_result.emit(self.result)


    def stop(self):
        None