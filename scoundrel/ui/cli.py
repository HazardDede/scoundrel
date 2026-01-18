import os
import functools
from scoundrel.builders import StandardDeckBuilder
from scoundrel.engines import StandardRulesEngine
from scoundrel import models


class ScoundrelCLI:
    def __init__(self):
        self.builder = StandardDeckBuilder()
        self.engine = StandardRulesEngine()
        self.state = models.GameState(
            player=models.Player(),
            deck=self.builder.build(shuffle=True),
            room=models.Room(),
        )
        self.engine.handle_next_room(self.state)

    def clear_screen(self):
        # English comment: Clear terminal for Windows (cls) or Unix (clear)
        os.system('cls' if os.name == 'nt' else 'clear')

    def draw_ui(self):
        self.clear_screen()
        print("=" * 40)
        print(f" SCOUNDREL - CLI EDITION ")
        print("=" * 40)
        
        # Player Stats
        p = self.state.player
        weapon_str = "Fäuste"
        if p.has_weapon:
            w = p.equipped
            last = w.slain_monsters[-1].rank if w.slain_monsters else "Neu"
            weapon_str = f"{w.weapon.name} ({last})"
            
        print(f"❤️  HP: {p.current_life}/{p.max_life} | ⚔️  Waffe: {weapon_str}")
        print(f"🃏 Deck: {self.state.deck.remaining} Karten übrig")
        print("-" * 40)
        
        # Room Cards
        print("IM RAUM:")
        for i, card in enumerate(self.state.room.cards, 1):
            print(f"[{i}] {card.name}")
        print("-" * 40)

    def get_actions(self, card_idx):
        # English comment: Maps card index to available engines actions
        if not (0 <= card_idx < len(self.state.room.cards)):
            return []
            
        card = self.state.room.cards[card_idx]
        actions = []

        if isinstance(card, models.Monster):
            # Bare handed
            p_fist = self.engine.preview_attack(self.state, card, False)
            actions.append({
                "label": f"Mit Fäusten angreifen (-{p_fist.damage_taken} HP)",
                "cmd": functools.partial(self.engine.handle_monster_attack, self.state, card, False)
            })
            # Weapon
            if self.engine.can_attack_monster(self.state, card, True):
                p_wep = self.engine.preview_attack(self.state, card, True)
                actions.append({
                    "label": f"Mit Waffe angreifen (-{p_wep.damage_taken} HP)",
                    "cmd": functools.partial(self.engine.handle_monster_attack, self.state, card, True)
                })

        elif isinstance(card, models.Potion):
            if self.engine.can_drink_potion(self.state, card):
                p_heal = self.engine.preview_potion(self.state, card)
                actions.append({
                    "label": f"Trinken (+{p_heal.healing_received} HP)",
                    "cmd": functools.partial(self.engine.handle_drink_potion, self.state, card)
                })

        elif isinstance(card, models.Weapon):
            actions.append({
                "label": "Waffe ausrüsten",
                "cmd": functools.partial(self.engine.handle_equip_weapon, self.state, card)
            })
            
        return actions

    def play(self):
        while not self.state.player.is_dead:
            # Check Victory
            highscore = self.engine.is_victory(self.state)
            if highscore is not None:
                print(f"🏆 SIEG! Du hast den Dungeon überlebt! Dein Highscore: {highscore}")
                break

            self.draw_ui()
            
            # Additional global actions
            can_flee = self.engine.can_flee_room(self.state)
            if can_flee:
                print("[F] Fliehen")

            choice = input("\nWähle eine Karte (1-4) oder Aktion: ").lower()

            if choice == 'f' and can_flee:
                self.engine.handle_flee_room(self.state)
                self.engine.handle_next_room(self.state)
                continue

            try:
                idx = int(choice) - 1
                actions = self.get_actions(idx)
                
                if not actions:
                    continue
                
                # If only one action, execute immediately, otherwise ask
                if len(actions) == 1:
                    actions[0]["cmd"]()
                else:
                    for i, a in enumerate(actions, 1):
                        print(f"  {i}: {a['label']}")
                    sub_choice = int(input("Aktion wählen: ")) - 1
                    actions[sub_choice]["cmd"]()

                # Auto-Refill Room
                if self.engine.next_room_available(self.state):
                    self.engine.handle_next_room(self.state)

            except (ValueError, IndexError):
                continue

        highscore = self.engine.is_game_over(self.state)
        if highscore is not None:
            self.draw_ui()
            print(f"\n💀 GAME OVER. Dein Abenteuer endet hier. Dein Highscore: {highscore}")


if __name__ == "__main__":
    game = ScoundrelCLI()
    game.play()