@echo off
echo ========================================
echo    BIT BY BIT - Information Theory
echo ========================================
echo.
echo Starting game with all features:
echo - Generators, Upgrades, Rebirth System
echo - Compression Era, Dual Currency
echo - Rich Visual Effects and Animations
echo.
echo Using launcher to prevent console artifacts...
python launcher.py
if errorlevel 1 (
    echo.
    echo Error: Could not start game
    echo Make sure Python and Pygame are installed
    pause
)
exit