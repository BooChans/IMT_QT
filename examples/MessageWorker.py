from PyQt5.QtCore import QThread, pyqtSignal

class MessageWorker(QThread):
    message_emitted = pyqtSignal(str)
    finished_with_result = pyqtSignal(object)  # Add this signal to emit results


    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

        def message_callback(text):
            self.message_emitted.emit(str(text))

        self.kwargs["message_callback"] = message_callback

    def run(self):
        result = self.func(*self.args, **self.kwargs)
        self.finished_with_result.emit(result)

        