import os
from pathlib import Path

import PyInstaller.__main__

if __name__ == "__main__":
    current_env_pip_path = Path(os.environ["CONDA_PREFIX"]) / "Lib/site-packages"
    ocr_model_path = Path(".paddleocr")
    paddle_fluid_proto_path = Path("paddle/fluid/proto")
    icon_path = Path("utils/icon.png")
    PyInstaller.__main__.run(
        [
            "main.py",
            # "--clean",
            "--onedir",  # Create a one-folder bundle containing an executable
            "--windowed",
            "--name=dopa",  # Name of the program
            "--log-level=WARN",  # Show less logging infor
            f"--icon={icon_path.with_suffix('.ico')}",
            f"--add-data={icon_path};utils",
            f"--add-data={ocr_model_path};{ocr_model_path}",  # Contains OCR models
            f"--add-data={current_env_pip_path / paddle_fluid_proto_path};{paddle_fluid_proto_path}",
            f"--add-binary={current_env_pip_path / 'paddle/libs'};.",
            f"--paths={current_env_pip_path / 'paddleocr'};{current_env_pip_path / 'paddle/libs'}",
            "--additional-hooks-dir=pyinstaller-hooks",
            "--exclude-module=matplotlib",
            # "--upx-dir=utils",  # Compress the .exe file  # FIXME: Right now compressing the EXE file will cause error
        ]
    )
