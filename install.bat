@echo off

:: Upgrade pip
python -m pip install --upgrade pip

:: Install dependencies from requirements.txt
pip install -r requirements.txt

:: Uninstall existing PyTorch packages (run twice to ensure clean removal)
pip uninstall -y torch torchvision torchaudio
pip uninstall -y torch torchvision torchaudio

:: Install PyTorch with CUDA 12.1 support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo Installation complete.
pause
