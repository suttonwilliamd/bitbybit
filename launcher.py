#!/usr/bin/env python3
"""
Windows launcher for Bit by Bit Game
Properly closes console window when game exits
"""

import sys
import os
import subprocess


def main():
    # Hide console window on Windows
    if sys.platform == "win32":
        import ctypes

        # Get console window handle
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32

        # Find and hide console window
        hwnd = kernel32.GetConsoleWindow()
        if hwnd:
            user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE

    # Run the actual game
    try:
        # Import and run the game
        from main import main as game_main

        game_main()
    except Exception as e:
        print(f"Error starting game: {e}")
        input("Press Enter to exit...")
    finally:
        # Clean exit on Windows
        if sys.platform == "win32":
            import ctypes

            ctypes.windll.user32.PostQuitMessage(0)


if __name__ == "__main__":
    main()
