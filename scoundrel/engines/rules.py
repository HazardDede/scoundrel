"""
Rules engine for Scoundrel.

This module governs the game logic, including combat calculations,
potion effects, equipment rules, and room transitions. It defines the
interface for rule validation and state updates.
"""

from abc import ABC, abstractmethod
from typing import Optional

from scoundrel.models import ActionPreview, GameState, HighScore, Monster, Potion, Weapon, EquippedWeapon


class RulesEngine(ABC):
    """
    Abstract interface for Scoundrel rules.

    Defines the contract for validating actions (can_...) and
    executing them (handle_...), ensuring consistency across
    different game variants.
    """

    # --- Game Status ---

    @abstractmethod
    def is_game_over(self, state: GameState) -> HighScore | None:
        """
        Player is dead or a different you lose the game situation has happened.

        Args:
            state (GameState): The state of the game.

        Returns:
            The high score that was reached if the game is over; otherwise None.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_victory(self, state: GameState) -> HighScore | None:
        """
        Player is victorious and the game ends.

        Args:
            state (GameState): The state of the game.

        Returns:
            The high score that was reached if the game is over; otherwise None.
        """
        raise NotImplementedError()

    # --- Combat Logic ---

    @abstractmethod
    def preview_attack(self, state: GameState, monster: Monster, use_weapon: bool) -> ActionPreview:
        """Calculates what would happen if the player attacks this monster."""
        raise NotImplementedError()

    @abstractmethod
    def can_attack_monster(self, state: GameState, monster: Monster, use_weapon: bool) -> bool:
        """Checks if the player is allowed to attack the given monster."""
        raise NotImplementedError()

    @abstractmethod
    def handle_monster_attack(self, state: GameState, monster: Monster, use_weapon: bool) -> None:
        """Executes the attack, calculates damage, and updates player/room state."""
        raise NotImplementedError()

    # --- Potion Logic ---

    @abstractmethod
    def preview_potion(self, state: GameState, potion: Potion) -> ActionPreview:
        """Calculates healing (considering HP cap)."""
        raise NotImplementedError()

    @abstractmethod
    def can_drink_potion(self, state: GameState, potion: Potion) -> bool:
        """Checks if the player can use a potion (e.g., limit per room)."""
        raise NotImplementedError()

    @abstractmethod
    def handle_drink_potion(self, state: GameState, potion: Potion) -> None:
        """Applies healing logic and marks the potion as used in the room."""
        raise NotImplementedError()

    # --- Equipment Logic ---
    @abstractmethod
    def can_equip_weapon(self, state: GameState, weapon: Weapon) -> bool:
        """Checks if a weapon can be equipped (usually always possible in a room)."""
        raise NotImplementedError()

    @abstractmethod
    def handle_equip_weapon(self, state: GameState, weapon: Weapon) -> None:
        """Replaces the current weapon and handles the discarded one."""
        raise NotImplementedError()

    # --- Movement & Room Logic ---
    @abstractmethod
    def can_flee_room(self, state: GameState) -> bool:
        """Checks if fleeing is allowed (4 cards present, not fled last room)."""
        raise NotImplementedError()

    @abstractmethod
    def handle_flee_room(self, state: GameState) -> None:
        """Moves room cards to the bottom of the deck and resets room state."""
        raise NotImplementedError()

    @abstractmethod
    def next_room_available(self, state: GameState) -> bool:
        """Determines if the room needs new cards (usually when <= 1 card remains)."""
        raise NotImplementedError()

    @abstractmethod
    def handle_next_room(self, state: GameState) -> None:
        """Moves to the next room."""
        raise NotImplementedError()


class StandardRulesEngine(RulesEngine):
    """
    Implementation of the classic Scoundrel rules.

    Includes rules for weapon effectiveness (descending monster ranks)
    and the single-potion-per-room healing limit.
    """

    # --- Game Status ---

    def is_game_over(self, state: GameState) -> HighScore | None:
        if state.player.current_life > 0:
            return None

        penalty = sum(
            card.strength for card in state.deck.cards if isinstance(card, Monster)
        )
        return state.player.current_life - penalty

    def is_victory(self, state: GameState) -> HighScore | None:
        if state.deck.remaining > 0:
            return None
        if state.room.remaining > 1:
            return None

        bonus = sum(
            card.potency for card in state.room.cards if isinstance(card, Potion)
        )

        return state.player.current_life + bonus

    # --- Combat Logic ---

    def preview_attack(self, state: GameState, monster: Monster, use_weapon: bool) -> ActionPreview:
        weapon = state.player.equipped
        damage = self._monster_damage(monster, weapon, use_weapon)

        return ActionPreview(
            damage_taken=damage,
            is_lethal=damage >= state.player.current_life
        )

    def can_attack_monster(self, state: GameState, monster: Monster, use_weapon: bool) -> bool:
        """
        Validates if an attack on a specific monster is possible.
        """
        # 1. Is the monster actually in the current room?#
        if not state.room.exists(monster):
            return False

        # 2. If the player wants to use a weapon, they must actually HAVE one equipped.
        # Prevention of illegal UI states where 'use_weapon' is toggled without a weapon
        if use_weapon and not state.player.has_weapon:
            return False

        # 3. You cannot attack with your equipped weapon if the rank of the current monster >= last slain monster rank.
        if use_weapon and state.player.equipped and not self._weapon_effective(monster, state.player.equipped):
            return False

        # 4. Standard Scoundrel: You can always attack (even if it leads to death).
        # Some variants might prevent "suicide moves", but standard rules allow it.
        return True

    def handle_monster_attack(self, state: GameState, monster: Monster, use_weapon: bool) -> None:
        # 1. Get preview to know the damage
        preview = self.preview_attack(state, monster, use_weapon)

        # 2. Apply damage
        state.player.current_life -= preview.damage_taken

        # 3. If weapon was used, update its history
        if use_weapon and state.player.equipped:
            state.player.equipped.slain_monsters.append(monster)

        # 4. Remove monster from room
        state.room.interacted(monster)

    # --- Potion Logic ---

    def preview_potion(self, state: GameState, potion: Potion) -> ActionPreview:
        """
        Calculates the healing effect.
        Standard Scoundrel: Healing cannot exceed max_health.
        """
        # Standard Scoundrel rule: only the first potion in a room heals.
        # Any subsequent potion in the same room is effectively wasted/unavailable.
        if state.room.potions_used > 0:
            return ActionPreview()

        current_hp = state.player.current_life
        max_hp = state.player.max_life

        # Calculate potential healing without exceeding max_health
        # If rank is 5 and we have 18/20, actual_healing is 2.
        potential_new_hp = min(max_hp, current_hp + potion.potency)
        actual_healing = potential_new_hp - current_hp

        return ActionPreview(
            healing_received=actual_healing,
        )

    def can_drink_potion(self, state: GameState, potion: Potion) -> bool:
        """
        Validates if a potion can be used for healing.
        Standard Scoundrel Rule: Only the first potion in a room provides healing.
        """
        # Standard Scoundrel rule: only the first potion heals.
        # Any subsequent potion in the same room is effectively wasted/unavailable.
        # But you can still "drink" which will discard the potion
        # To avoid any UI inconcistencies you can always "drink"
        return state.room.exists(potion)

    def handle_drink_potion(self, state: GameState, potion: Potion) -> None:
        """
        Applies healing and updates the game state.
        """
        # 1. Preview nutzen, um die tatsächliche Heilung zu berechnen
        preview = self.preview_potion(state, potion)

        # 2. HP anpassen
        state.player.current_life += preview.healing_received

        # 3. Den Raum-Zähler für Tränke erhöhen
        state.room.potions_used += 1

        # 4. Karte als interagiert markieren (aus dem Raum entfernen)
        state.room.interacted(potion)

    # --- Equip Logic ---

    def can_equip_weapon(self, state: GameState, weapon: Weapon) -> bool:
        """
        Validates if a weapon can be equipped.
        Standard Scoundrel: Possible if the card is in the current room.
        """
        # Check if the weapon card is physically present in the room
        return state.room.exists(weapon)

    def handle_equip_weapon(self, state: GameState, weapon: Weapon) -> None:
        """
        Replaces the player's current weapon with a new one.
        The old weapon and its combat history are discarded.
        """
        if not self.can_equip_weapon(state, weapon):
            return

        # Create a fresh EquippedWeapon instance.
        # This implicitly clears the 'slain_monsters' history.
        state.player.equipped = EquippedWeapon(weapon=weapon)

        # English comment: Remove the weapon card from the room
        state.room.interacted(weapon)

    # --- Movement and Flee Logic ---

    def can_flee_room(self, state: GameState) -> bool:
        """
        Checks if fleeing is allowed according to Scoundrel rules.
        """
        # 1. Fleeing is only possible before interacting with any card in the current room
        if len(state.room.cards) != 4:
            return False

        # 2. The state must track if the 'flee' action was used in the last room cycle
        if state.last_room_fled:
            return False

        return True

    def handle_flee_room(self, state: GameState) -> None:
        """
        Executes the flee action: moves room cards to the bottom and resets state.
        """
        if not self.can_flee_room(state):
            return

        # 1. Move all cards from the room back to the bottom of the deck
        state.deck.to_bottom(state.room.cards)

        # 2. Empty the room
        state.room.cards = []

        # 3. Mark this room as 'fled' to prevent back-to-back fleeing
        state.last_room_fled = True

    def next_room_available(self, state: GameState) -> bool:
        """
        Determines if the player is allowed to draw new cards for a room.
        Standard Scoundrel: Possible if 0 or 1 card is left in the room.
        """
        # You can only 'refill' the room if it's nearly empty.
        # Exception: If handle_flee_room was just called, room.cards is already [].
        return len(state.room.cards) <= 1

    def handle_next_room(self, state: GameState) -> None:
        """
        Transitions to the next room by drawing 4 cards and resetting room stats.
        """
        if not self.next_room_available(state):
            return

        # 1. Reset room-specific state
        # Important: If the player enters a room NORMALLY (not fleeing),
        # we reset the last_room_fled flag so they can flee again in the NEXT room.
        if len(state.room.cards) != 0:
            state.last_room_fled = False

        state.room.potions_used = 0

        # 2. Draw 4 cards from the deck (or as many as are left)
        # English comment: Fill the room up to 4 cards.
        while len(state.room.cards) < 4 and state.deck.remaining > 0:
            new_card = state.deck.draw()
            state.room.cards.append(new_card)

    # --- Utility stuff ---

    def _weapon_effective(self, monster: Monster, weapon: EquippedWeapon) -> bool:
        # Standard Scoundrel Rule:
        # Weapon is only effective if current monster rank < last slain monster rank.
        # If no monster was slain yet, it's always effective.

        if weapon.last_slain_monster is None:  # No monster slain so far -> Weapon is effective
            return True
        # current monster rank < last slain one
        if monster.rank < weapon.last_slain_monster.rank:  # type: ignore
            return True
        return False

    def _monster_damage(self, monster: Monster, weapon: Optional[EquippedWeapon], use_weapon: bool) -> int:
        if not use_weapon:  # Fight bare-handed
            return monster.strength
        if not weapon:  # No weapon equipped
            return monster.strength
        weapon_effective = self._weapon_effective(monster, weapon)
        return max(0, monster.strength - weapon.weapon.protection) if weapon_effective else monster.strength
