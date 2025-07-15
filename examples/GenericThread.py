from PyQt5.QtCore import QThread, pyqtSignal
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
            self.progress_changed.emit(percent)

        self.kwargs["callback"] = progress_callback
        self.result = None


    def run(self):
        self.result = self.func(*self.args, **self.kwargs)
        self.finished_with_result.emit(self.result)


    def stop(self):
        None