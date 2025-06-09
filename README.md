# PyQt Screen Capture

A screen capture utility that works with PyQt6, PySide6, PyQt5, PySide2, and PySide.

## Features

- Cross-platform (Windows, Linux, macOS, etc.)
- Supports Python 2+
- Automatically detects available Qt bindings
- Memory-efficient screen capture using shared ndarrays in OpenCV-compatible HWC BGRX 8888 format
- Simple generator-based interface

## Installation

Make sure you have PyQt6, PySide6, PyQt5, PySide2, or PySide installed.

Then install `pyqt-screen-capture`:

```bash
pip install pyqt-screen-capture
```

## Usage

### Capture single frame

```python
from pyqt_screen_capture import hwc_bgrx_8888_screen_capturer

screen_capturer = hwc_bgrx_8888_screen_capturer()

# Get next screen frame (as numpy array in HWC BGRX 8888 format)
frame = next(screen_capturer)

# Example: Convert to RGB and display with matplotlib
import matplotlib.pyplot as plt

plt.imshow(frame[:, :, [2, 1, 0]])  # Convert BGR to RGB
plt.show()
```

### Continuous capture

```python
import cv2

from pyqt_screen_capture import hwc_bgrx_8888_screen_capturer

for frame in hwc_bgrx_8888_screen_capturer():
    # Process frame (OpenCV, etc.)
    cv2.imshow('Screen Capture', frame[:, :, :3])  # Use BGR channels only
    key = cv2.waitKey()
    if key & 0xFF == ord('q'):
        break
```

### Caveat

You MUST use the shared ndarray between yields, as the underlying buffer is freed afterward:

```python
from pyqt_screen_capture import hwc_bgrx_8888_screen_capturer
screen_capturer = hwc_bgrx_8888_screen_capturer()
r1 = next(screen_capturer)
# OK to use r1 here
r2 = next(screen_capturer)
# OK to use r2 here, DO NOT USE r1 HERE!
```

## Acknowledgments

This project modifies code automatically determining which Qt package to use from [pyqtgraph](https://github.com/pyqtgraph/pyqtgraph), available under the [MIT License](https://github.com/pyqtgraph/pyqtgraph/blob/master/LICENSE.txt)

## Contributing

Contributions are welcome!  Please submit pull requests or open issues on GitHub.

## License

This project is licensed under the [MIT License](LICENSE). See the [LICENSE](LICENSE) file for details.