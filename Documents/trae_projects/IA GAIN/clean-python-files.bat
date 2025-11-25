@echo off
echo Removendo arquivos grandes do Python...

:: Remover diretório .venv311 completamente
if exist .venv311 (
    echo Removendo .venv311...
    rmdir /s /q .venv311
)

:: Remover outros arquivos grandes se existirem
if exist xgboost.dll del /f xgboost.dll
if exist *.pyd del /f *.pyd

echo Limpeza concluída!
echo Agora você pode fazer o deploy novamente.