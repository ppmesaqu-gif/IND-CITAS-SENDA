@echo off
echo ===============================================
echo  COMPILAR GENERADOR DE INFORMES A .EXE
echo  Planta Entrerrios - Alpina  v4.0
echo ===============================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instale Python 3.9+
    pause & exit /b 1
)

:: Instalar/actualizar PyInstaller y dependencias
echo [1/4] Instalando dependencias...
python -m pip install pyinstaller pandas openpyxl python-pptx matplotlib pillow lxml numpy --quiet
if errorlevel 1 ( echo ERROR instalando dependencias & pause & exit /b 1 )

:: Limpiar compilaciones anteriores
echo [2/4] Limpiando compilaciones anteriores...
if exist "build" rmdir /s /q build
if exist "dist"  rmdir /s /q dist
if exist "generar_informe.spec" del /q generar_informe.spec

:: Compilar
echo [3/4] Compilando .exe (puede tardar 3-6 minutos)...
pyinstaller ^
  --onefile ^
  --windowed ^
  --icon=Imagen1.ico ^
  --name="GeneradorInformes_Alpina" ^
  --add-data="utils_datos.py;." ^
  --add-data="dashboard_operativo.py;." ^
  --add-data="dashboard_gerencial.py;." ^
  --add-data="pptx_generador.py;." ^
  --add-data="Imagen1.ico;." ^
  --hidden-import=pandas ^
  --hidden-import=openpyxl ^
  --hidden-import=openpyxl.styles ^
  --hidden-import=openpyxl.utils ^
  --hidden-import=openpyxl.cell ^
  --hidden-import=openpyxl.workbook.child ^
  --hidden-import=openpyxl.drawing.image ^
  --hidden-import=pptx ^
  --hidden-import=pptx.oxml ^
  --hidden-import=pptx.oxml.ns ^
  --hidden-import=pptx.util ^
  --hidden-import=pptx.dml.color ^
  --hidden-import=pptx.enum.text ^
  --hidden-import=matplotlib ^
  --hidden-import=matplotlib.pyplot ^
  --hidden-import=matplotlib.backends.backend_agg ^
  --hidden-import=numpy ^
  --hidden-import=numpy.core ^
  --hidden-import=PIL ^
  --hidden-import=PIL.Image ^
  --hidden-import=lxml ^
  --hidden-import=lxml.etree ^
  --hidden-import=babel.numbers ^
  --collect-all=openpyxl ^
  --collect-all=pandas ^
  --collect-all=pptx ^
  --collect-all=lxml ^
  --collect-all=matplotlib ^
  --noconfirm ^
  generar_informe.py

if errorlevel 1 ( echo ERROR al compilar & pause & exit /b 1 )

:: Copiar assets si existen
if exist "assets" (
    echo Copiando carpeta assets...
    xcopy /e /i /q "assets" "dist\assets"
)

echo [4/4] Listo!
echo.
echo El ejecutable esta en:  dist\GeneradorInformes_Alpina.exe
echo.
pause
