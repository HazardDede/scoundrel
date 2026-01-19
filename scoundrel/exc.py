"""
Custom exception definitions for the Scoundrel game engine.

This module provides specific error types to distinguish between
engine logic failures and valid game-state transitions.
"""


class ScoundrelError(Exception):
    """Base class for all exceptions raised by the Scoundrel engine."""


class DeckEmptyError(ScoundrelError):
    """
    Raised when an operation attempts to draw from or interact with an empty deck.

    This usually occurs during the 'Room Refill' phase if the game logic
    does not correctly check for the 'is_empty' state of the Deck model.
    """


class InvalidActionError(ScoundrelError):
    """
    Raised when a player attempts an illegal move.

    Examples include trying to slay a monster higher than the last one
    with the same weapon, or trying to use two potions in the same room.
    """
