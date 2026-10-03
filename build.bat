@echo off
echo =========================================
echo COMPILANDO SISTEMA HUAUCKE
echo =========================================

echo Instalando / Verificando dependencias...
pip install -r requirements.txt

echo.
echo Limpiando compilaciones anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Generando ejecutable (Onefile)...
python -m PyInstaller --noconfirm --onefile --windowed --icon="logo.ico" --name "Huaucke" --add-data "logo.jpg;." main.py

echo.
echo =========================================
echo COMPILACION TERMINADA
echo El ejecutable esta en la carpeta "dist\Huaucke.exe"
echo =========================================
pause
