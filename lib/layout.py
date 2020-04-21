from PySide2.QtWidgets import *

class Layout:
    @staticmethod
    def add_spacer(layout):
      # w, h
      vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding) 
      layout.addSpacerItem(vertical_spacer)
      return layout

# Signals:
# message.returnPressed.connect(send_message)
# timer = QTimer()
# timer.timeout.connect(display_new_messages)
# timer.start(1000)
# return app
