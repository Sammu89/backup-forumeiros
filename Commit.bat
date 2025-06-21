@echo off
setlocal enabledelayedexpansion

REM Ir para a pasta onde está este script
cd /d "%~dp0"

REM Verificar se o Git está configurado
git config --global user.email >nul 2>&1
if errorlevel 1 (
    echo Configurando Git pela primeira vez...
    git config --global user.email "samuel.leca@gmail.com"
    git config --global user.name "Sammu89"
    echo Git configurado com sucesso!
    echo.
) else (
    REM Verificar se já tem as configurações corretas
    for /f "delims=" %%i in ('git config --global user.email') do set current_email=%%i
    for /f "delims=" %%i in ('git config --global user.name') do set current_name=%%i
    
    if not "!current_email!"=="samuel.leca@gmail.com" (
        echo Atualizando configuração de email...
        git config --global user.email "samuel.leca@gmail.com"
    )
    
    if not "!current_name!"=="Sammu89" (
        echo Atualizando configuração de nome...
        git config --global user.name "Sammu89"
    )
)

REM Adicionar tudo (inclusive se tiveres modificado o .gitignore)
echo Adicionando arquivos...
git add .

REM Gerar comentário com data e hora
for /f "tokens=1-5 delims=/ " %%a in ("%date% %time%") do (
    set commitmsg=Commit automático - %%a-%%b-%%c às %%d:%%e
)

REM Fazer commit
echo Fazendo commit...
git commit -m "!commitmsg!"
if errorlevel 1 (
    echo Erro no commit ou nenhuma alteração para commitar.
    pause
    exit /b 1
)

REM Fazer push
echo Enviando para o repositório...
git push origin main
if errorlevel 1 (
    echo Erro no push. Verifique sua autenticação ou conexão.
    echo.
    echo Se for a primeira vez, talvez precises autenticar no Git:
    echo - Para HTTPS: o Git vai pedir username/password ou token
    echo - Para SSH: certifica-te que tens a chave SSH configurada
    pause
    exit /b 1
)

echo.
echo Commit feito e enviado com sucesso!
pause