from scoundrel.builders import StandardBuilder
from scoundrel.engine import StandardRulesEngine
from scoundrel import models

import functools 


def print_player(state):
    print(f"LP: {state.player.current_life} / {state.player.max_life}")
    if state.player.has_weapon:
        weapon = state.player.weapon
        monster_rank = weapon.last_slain_monster.rank if weapon.last_slain_monster else 'unbenutzt'
        print(f"Waffe: {weapon.weapon.name} ({monster_rank})")

def print_current_room(state):
    for i, card in enumerate(state.room.cards, 1):
        print(f"{i}. {card.name}")

def print_available_actions(actions):
    for i, action in enumerate(actions, 1):
        print(f"{i}: {action[0]}")

def perform_action(idx, actions):
    if not(0 < idx <= len(actions)):
        return
    _, fun = actions[idx - 1]
    fun()


def available_monster_actions(state, engine, monster: models.Monster):
    bare_handed_attack = engine.can_attack_monster(state, monster, False)
    weapon_attack = engine.can_attack_monster(state, monster, True)
    
    actions = []
    if bare_handed_attack:
        fun = functools.partial(
            engine.handle_monster_attack, state=state, monster=monster, use_weapon=False
        )
        preview = engine.preview_attack(state, monster, False)
        actions.append((f"Angriff mit den Fäusten (-{preview.damage_taken} LP)", fun))
    if weapon_attack:
        fun = functools.partial(
            engine.handle_monster_attack, state=state, monster=monster, use_weapon=True
        )
        preview = engine.preview_attack(state, monster, True)
        actions.append((f"Angriff mit der Waffe (-{preview.damage_taken} LP)", fun))

    return actions


def available_potion_actions(state, engine, potion: models.Potion):
    if not engine.can_drink_potion(state, potion):
        return []

    preview = engine.preview_potion(state, potion)
    return [(
        f"Trinken (+{preview.healing_received}) LP", 
        functools.partial(engine.handle_drink_potion, state=state, potion=potion)
    )]


def available_weapon_actions(state, engine, weapon: models.Weapon):
    if not engine.can_equip_weapon(state, weapon):
        return []

    return [(
        "Ausrüsten",
        functools.partial(engine.handle_equip_weapon, state=state, weapon=weapon)
    )]


def available_actions(state, engine, selection: int):
    if not (0 < selection <= state.room.remaining):
        return
    
    sel_card = state.room.cards[selection - 1]
    if isinstance(sel_card, models.Monster):
        return available_monster_actions(state, engine, sel_card)
    if isinstance(sel_card, models.Potion):
        return available_potion_actions(state, engine, sel_card)
    if isinstance(sel_card, models.Weapon):
        return available_weapon_actions(state, engine, sel_card)

    
builder = StandardBuilder()
engine = StandardRulesEngine()
state = models.GameState(
    player=models.Player(),
    deck=builder.build_deck(shuffle=True),
    room=models.Room(),
)

engine.handle_next_room(state)


while True:
    print_player(state)
    print_current_room(state)

    if state.player.is_dead:
        print("GAME OVER")
        break

    try:
        selection = int(input("Eingabe: "))
    except ValueError:
        pass
    
    actions = available_actions(state, engine, selection)
    if engine.can_flee_room(state):
        actions.append((
            'Fliehen',
            functools.partial(engine.handle_flee_room, state=state)
        ))
    if actions:
        print_available_actions(actions)
        try:
            selection = int(input("Eingabe: "))
        except ValueError:
            continue
        perform_action(selection, actions)


    if state.deck.remaining <= 0:
        print("DU BIST LEBEND AUS DEM DUNGEON ENTKOMMEN")
        break

    if engine.next_room_available(state):
        engine.handle_next_room(state)


