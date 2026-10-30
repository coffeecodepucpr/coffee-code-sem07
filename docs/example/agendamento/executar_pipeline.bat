@echo off
REM Executa o pipeline de coleta no Windows (NAO TESTADO: veja o Modulo 13).
REM Ajuste PROJETO para o caminho do SEU projeto. As aspas permitem espacos.
set "PROJETO=C:\Users\voce\projeto-coleta\pipeline"
if not exist "%PROJETO%\logs" mkdir "%PROJETO%\logs"
cd /d "%PROJETO%"
"%PROJETO%\.venv\Scripts\python.exe" -m coleta %* >> "%PROJETO%\logs\agendador.log" 2>&1
exit /b %ERRORLEVEL%
