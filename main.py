"""
Main entry point for Bit by Bit Game
"""

import pygame
import sys
import os
from gui import BitByBitGame


def main():
    """Main entry point for the game"""
    # Initialize Pygame with console fix
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
    pygame.init()

    # Create and run the game
    game = BitByBitGame()
    game.run()


if __name__ == "__main__":
    main()
