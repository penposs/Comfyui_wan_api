@echo off
cd /d %~dp0
echo === WanAPI GitHub仓库清理工具 ===
python cleanup_github.py
pause 