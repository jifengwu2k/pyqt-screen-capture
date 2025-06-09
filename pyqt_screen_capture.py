import sys

import numpy as np

# Automatically determining which Qt package to use is adapted from [pyqtgraph](https://github.com/pyqtgraph/pyqtgraph)
# Original code is licensed under MIT License
PYQT6 = 'PyQt6'
PYSIDE6 = 'PySide6'
PYQT5 = 'PyQt5'
PYSIDE2 = 'PySide2'
PYSIDE = 'PySide'

QT_LIB_ORDER = [PYQT6, PYSIDE6, PYQT5, PYSIDE2, PYSIDE]

SELECTED_QT_LIB = None

# Check if any Qt lib is already imported
for qt_lib in QT_LIB_ORDER:
    if qt_lib in sys.modules:
        SELECTED_QT_LIB = qt_lib
        break

# Try importing if none found
if SELECTED_QT_LIB is None:
    for qt_lib in QT_LIB_ORDER:
        try:
            __import__(qt_lib)
            SELECTED_QT_LIB = qt_lib
            break
        except ImportError:
            pass

IS_PYQT = None

if SELECTED_QT_LIB == PYQT6:
    from PyQt6.QtGui import QImage, QPixmap, QScreen
    from PyQt6.QtWidgets import QApplication

    IS_PYQT = True
elif SELECTED_QT_LIB == PYSIDE6:
    from PySide6.QtGui import QImage, QPixmap, QScreen
    from PySide6.QtWidgets import QApplication

    IS_PYQT = False
elif SELECTED_QT_LIB == PYQT5:
    from PyQt5.QtGui import QImage, QPixmap, QScreen
    from PyQt5.QtWidgets import QApplication

    IS_PYQT = True
elif SELECTED_QT_LIB == PYSIDE2:
    from PySide2.QtGui import QImage, QPixmap, QScreen
    from PySide2.QtWidgets import QApplication

    IS_PYQT = False
elif SELECTED_QT_LIB == PYSIDE:
    from PySide.QtGui import QApplication, QDesktopWidget, QImage, QPixmap

    IS_PYQT = False
else:
    raise ImportError("We require one of PyQt6, PySide6, PyQt5, PySide2, or PySide; none of these packages could be imported.")


def get_or_create_q_application():
    """Get the existing QApplication instance or create a new one if none exists.

    Note:
        Only one QApplication instance can exist per process. Creating multiple instances will raise a RuntimeError.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


# Initialize Qt application
application = get_or_create_q_application()

# Set up `screen_width`, `screen_height`, and `grab_window` function
if SELECTED_QT_LIB == PYSIDE:
    desktop_widget = QDesktopWidget()
    window_id = desktop_widget.winId()
    screen_geometry = desktop_widget.screenGeometry()  # Returns QRect
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()

    def grab_window():
        return QPixmap.grabWindow(window_id, 0, 0, screen_width, screen_height)
else:
    primary_screen = QApplication.primaryScreen()
    screen_geometry = primary_screen.geometry()  # Returns QRect
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()

    def grab_window():
        return primary_screen.grabWindow(0, 0, 0, screen_width, screen_height)

# Set up `Format_RGB32` and `get_buffer` function
if IS_PYQT:
    Format_RGB32 = QImage.Format.Format_RGB32

    def get_buffer(qimage):
        pixel_data_view = qimage.constBits() # sip.voidptr
        size_in_bytes = qimage.sizeInBytes()

        # A voidptr may also be given a size (i.e. the size of the block of memory that is pointed to) by calling its setsize() method
        # If it has a size then it is also able to support Python's buffer protocol and behaves like a Python memoryview object
        pixel_data_view.setsize(size_in_bytes)

        return pixel_data_view
else:
    Format_RGB32 = QImage.Format_RGB32

    def get_buffer(qimage):
        return qimage.constBits() # memoryview


def hwc_bgrx_8888_screen_capturer():
    """Coroutine that yields screen captures as shared ndarrays

    Yields:
        numpy.ndarray: shared ndarrays in HWC BGRX 8888 format

    Notes:
        - Memory layout matches OpenCV's default BGR format
        - MUST use the shared ndarray between yields, as the underlying buffer is freed afterward:
        ```
        >>> screen_capturer = hwc_bgrx_8888_screen_capturer()
        >>> r1 = next(screen_capturer)
        >>> # OK to use r1 here
        >>> r2 = next(screen_capturer)
        >>> # OK to use r2 here, DO NOT USE r1 HERE!
        ```
    """
    while True:
        # Capture screen content
        screenshot = grab_window()
        qt_image = screenshot.toImage()
    
        # Convert to RGB32 format (actually BGRX in memory)
        if qt_image.format() != Format_RGB32:
            bgr32_image = qt_image.convertToFormat(Format_RGB32)
        else:
            bgr32_image = qt_image
    
        # Access buffer
        buffer = get_buffer(bgr32_image)
    
        # Convert to ndarray (shape: height x width x 4 channels)
        # Channel order: Blue, Green, Red, unused (BGRX)
        bgrx_array_view = np.frombuffer(buffer, dtype=np.uint8).reshape(screen_height, screen_width, 4)
    
        yield bgrx_array_view
