@echo off
title Instalador Sistema Huaucke
echo ===================================================
echo        INSTALADOR DEL SISTEMA - HUAUCKE
echo ===================================================
echo.

REM 1. Crear carpeta del sistema en C:\Huaucke
echo [1/3] Preparando directorio C:\Huaucke...
if not exist "C:\Huaucke" (
    mkdir "C:\Huaucke"
    echo       Directorio creado correctamente.
) else (
    echo       Directorio C:\Huaucke ya existe.
)

REM 2. Instalar base de datos (solo si no existe previamente)
echo [2/3] Verificando base de datos del negocio...
if not exist "C:\Huaucke\database.sqlite" (
    if exist "%~dp0database.sqlite" (
        copy /y "%~dp0database.sqlite" "C:\Huaucke\database.sqlite" >nul
        echo       Base de datos inicial instalada con exito.
    ) else (
        echo       AVISO: No se encontro database.sqlite junto al instalador.
    )
) else (
    echo       Base de datos existente detectada. Protegida para no perder datos.
)

REM 3. Copiar ejecutable y crear acceso directo en el Escritorio
echo [3/3] Instalando Huaucke.exe...
if exist "%~dp0Huaucke.exe" (
    copy /y "%~dp0Huaucke.exe" "C:\Huaucke\Huaucke.exe" >nul
    powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([System.IO.Path]::Combine([Environment]::GetFolderPath('Desktop'), 'Huaucke POS.lnk')); $s.TargetPath = 'C:\Huaucke\Huaucke.exe'; $s.WorkingDirectory = 'C:\Huaucke'; $s.Save()" >nul 2>&1
    echo       Acceso directo "Huaucke POS" creado en el Escritorio.
) else (
    echo       AVISO: No se encontro Huaucke.exe en esta carpeta.
)

echo.
echo ===================================================
echo        INSTALACION COMPLETADA CON EXITO
echo ===================================================
echo Ya puedes iniciar el sistema desde el acceso directo del Escritorio.
echo.
pause
