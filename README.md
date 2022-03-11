# document-process-automation
## Requirements:
Task 1: Create an app that is able to:
    + Input PDF files.
    + Split 3 pages into 1 file.
    + User select the region contains new name.
    + Rename and save the new PDF files.

    
Task 2: Create an app that is able to:
      + Input PDF files.
      + Split 1 pages into 1 file.
      + User select the region contains new name.
      + Rename and save the new PDF files.

## Development environment
```[bash]
conda env create -f environment.yml
conda activate doc-process-auto
pip install utils\Shapely-1.8.1.post1-cp38-cp38-win_amd64.whl --force-reinstall
```

# Build EXE files
- Locate where your site-packges folder that contains installed libraries is.
- Edit "paddle\dataset\image.py" to become:
```[python]
# if six.PY3:
#     import subprocess
#     import sys
#     import os
#     interpreter = sys.executable
#     # Note(zhouwei): if use Python/C 'PyRun_SimpleString', 'sys.executable'
#     # will be the C++ execubable on Windows
#     if sys.platform == 'win32' and 'python.exe' not in interpreter:
#         interpreter = sys.exec_prefix + os.sep + 'python.exe'
#     import_cv2_proc = subprocess.Popen(
#         [interpreter, "-c", "import cv2"],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE)
#     out, err = import_cv2_proc.communicate()
#     retcode = import_cv2_proc.poll()
#     if retcode != 0:
#         cv2 = None
#     else:
#         import cv2
# else:
try:
    import cv2
except ImportError:
    cv2 = None
```
- Edit "paddleocr\ppocr\utils\e2e_utils\pgnet_pp_utils.py"
```[python]
from .extract_textpoint_slow import *
from .extract_textpoint_fast import generate_pivot_list_fast, restore_poly
```
- Run `python build_exe.py`
