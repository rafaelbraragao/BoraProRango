@echo off
:: Detecta a branch atual
for /f %%i in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%i

echo 📂 Branch atual: %BRANCH%
echo 🔄 Limpando cache do Git...
git rm -r --cached .

echo ➕ Adicionando arquivos...
git add .

echo 💬 Fazendo commit...
set /p COMMIT_MSG="Digite a mensagem do commit: "
git commit -m "%COMMIT_MSG%"

echo 🚀 Enviando para o GitHub na branch '%BRANCH%'...
git push origin %BRANCH%

echo ✅ Push concluído com sucesso!
pause