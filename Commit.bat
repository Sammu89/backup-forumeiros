@echo off
setlocal enabledelayedexpansion

REM Ir para a pasta onde está este script
cd /d "%~dp0"

REM Adicionar tudo (inclusive se tiveres modificado o .gitignore)
git add .

REM Gerar comentário com data e hora
for /f "tokens=1-5 delims=/ " %%a in ("%date% %time%") do (
    set commitmsg=Commit automático - %%a-%%b-%%c às %%d:%%e
)

REM Fazer commit
git commit -m "!commitmsg!"

REM Fazer push
git push origin main

echo.
echo Commit feito e enviado com sucesso!
pause