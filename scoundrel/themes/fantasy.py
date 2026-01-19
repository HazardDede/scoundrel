"""
Fantasy-themed configuration for the Scoundrel game engine.

This module contains the FANTASY_ATLAS, which maps standard card ranks
and suits to a high-fantasy setting (Monsters, Potions, and Weapons),
and provides the pre-configured FantasyTheme.
"""

from functools import partial

from scoundrel.models import Suit
from .base import CardAtlas, CardIdentity, AtlasTheme


# Definition of the card identities based on suit and rank.
# This atlas serves as the lookup table for the FantasyTheme.
FANTASY_ATLAS: CardAtlas = {
    # --- Monsters (CLUBS)
    (Suit.CLUBS, 2): CardIdentity(name="Käfer", emoji="🪲"),
    (Suit.CLUBS, 3): CardIdentity(name="Skorpion", emoji="🦂"),
    (Suit.CLUBS, 4): CardIdentity(name="Spinne", emoji="🕷️"),
    (Suit.CLUBS, 5): CardIdentity(name="Wolf", emoji="🐺"),
    (Suit.CLUBS, 6): CardIdentity(name="Bär", emoji="🐻"),
    (Suit.CLUBS, 7): CardIdentity(name="Zombie", emoji="🧟"),
    (Suit.CLUBS, 8): CardIdentity(name="Geist", emoji="👻"),
    (Suit.CLUBS, 9): CardIdentity(name="Skelett", emoji="💀"),
    (Suit.CLUBS, 10): CardIdentity(name="Allsehendes Auge", emoji="👁️"),
    (Suit.CLUBS, 11): CardIdentity(name="Golem", emoji="🪨"),
    (Suit.CLUBS, 12): CardIdentity(name="Vampirlord", emoji="🧛‍"),
    (Suit.CLUBS, 13): CardIdentity(name="Dschinn", emoji="🧞"),
    (Suit.CLUBS, 14): CardIdentity(name="Drache", emoji="🐉"),

    # --- Monsters (SPADES)
    (Suit.SPADES, 2): CardIdentity(name="Fledermaus", emoji="🦇"),
    (Suit.SPADES, 3): CardIdentity(name="Schleim", emoji="🟢"),
    (Suit.SPADES, 4): CardIdentity(name="Schlange", emoji="🐍"),
    (Suit.SPADES, 5): CardIdentity(name="Raubvogel", emoji="🦅"),
    (Suit.SPADES, 6): CardIdentity(name="Alligator", emoji="🐊"),
    (Suit.SPADES, 7): CardIdentity(name="Pilzkopf", emoji="🍄"),
    (Suit.SPADES, 8): CardIdentity(name="Goblin", emoji="👹"),
    (Suit.SPADES, 9): CardIdentity(name="Riesenoktopus", emoji="🐙"),
    (Suit.SPADES, 10): CardIdentity(name="Gedankenschinder", emoji="🧠"),
    (Suit.SPADES, 11): CardIdentity(name="Feuerelementar", emoji="🔥"),
    (Suit.SPADES, 12): CardIdentity(name="Frostelementar", emoji="❄️"),
    (Suit.SPADES, 13): CardIdentity(name="Chaosgeist", emoji="🧞‍"),
    (Suit.SPADES, 14): CardIdentity(name="Blutdämon", emoji="🩸"),

    # --- Potions (HEARTS)
    (Suit.HEARTS, 2): CardIdentity(name="Heilkraut", emoji="🌿"),
    (Suit.HEARTS, 3): CardIdentity(name="Klarwasser", emoji="💧"),
    (Suit.HEARTS, 4): CardIdentity(name="Apfel", emoji="🍎"),
    (Suit.HEARTS, 5): CardIdentity(name="Kräutertrank", emoji="🧃"),
    (Suit.HEARTS, 6): CardIdentity(name="Wundsalbe", emoji="🩹"),
    (Suit.HEARTS, 7): CardIdentity(name="Goldener Honig", emoji="🍯"),
    (Suit.HEARTS, 8): CardIdentity(name="Heiltrank", emoji="🧪"),
    (Suit.HEARTS, 9): CardIdentity(name="Lebensessenz", emoji="💖"),
    (Suit.HEARTS, 10): CardIdentity(name="Erneuerungselixier", emoji="✨"),
    (Suit.HEARTS, 11): CardIdentity(name="Vitaltrank", emoji="🌱"),
    (Suit.HEARTS, 12): CardIdentity(name="Essenz der Lebenskraft", emoji="🔮"),
    (Suit.HEARTS, 13): CardIdentity(name="Elixier der Wiedergeburt", emoji="🌟"),
    (Suit.HEARTS, 14): CardIdentity(name="Herz des Lebens", emoji="💎"),

    # --- Weapons (DIAMONDS)
    (Suit.DIAMONDS, 2): CardIdentity(name="Knüppel", emoji="🪵"),
    (Suit.DIAMONDS, 3): CardIdentity(name="Dolch", emoji="🗡️"),
    (Suit.DIAMONDS, 4): CardIdentity(name="Handaxt", emoji="🪓"),
    (Suit.DIAMONDS, 5): CardIdentity(name="Kurzschwert", emoji="⚔️"),
    (Suit.DIAMONDS, 6): CardIdentity(name="Kriegshammer", emoji="🔨"),
    (Suit.DIAMONDS, 7): CardIdentity(name="Langschwert", emoji="🗡️"),
    (Suit.DIAMONDS, 8): CardIdentity(name="Streitaxt", emoji="🪓"),
    (Suit.DIAMONDS, 9): CardIdentity(name="Zweihänder", emoji="⚔️"),
    (Suit.DIAMONDS, 10): CardIdentity(name="Kriegsbogen", emoji="🏹"),
    (Suit.DIAMONDS, 11): CardIdentity(name="Feuerzahn (Legendär)", emoji="🔥"),
    (Suit.DIAMONDS, 12): CardIdentity(name="Frostbiss (Legendär)", emoji="❄️"),
    (Suit.DIAMONDS, 13): CardIdentity(name="Himmelszorn (Legendär)", emoji="⚡"),
    (Suit.DIAMONDS, 14): CardIdentity(name="Weltenbrecher (Legendär)", emoji="💎"),
}

# Pre-configured instance of AtlasTheme.
# Using functools.partial allows FantasyTheme to be instantiated
# without manually passing the FANTASY_ATLAS every time.
FantasyTheme = partial(AtlasTheme, atlas=FANTASY_ATLAS)
