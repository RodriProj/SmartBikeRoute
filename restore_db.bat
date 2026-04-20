@echo off
echo ==========================================
echo  SmartBikeRoutes - Restaurar Base de Dados
echo ==========================================
echo.

if not exist "smartbike_dump.dump" (
    echo ERRO: Ficheiro smartbike_dump.dump nao encontrado!
    echo Coloca o dump do Rodrigo nesta pasta e volta a correr.
    pause
    exit /b 1
)

echo A aguardar que o container da BD esteja pronto...
timeout /t 5 /nobreak >nul

echo A restaurar a base de dados...
docker exec -i smartbike_db pg_restore -U smartbike -d smartbike_vilareal2 --no-owner --role=smartbike < smartbike_dump.dump

echo.
echo Base de dados restaurada com sucesso!
pause
