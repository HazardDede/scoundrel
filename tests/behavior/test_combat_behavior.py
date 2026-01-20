from pytest_bdd import scenario


@scenario('features/combat.feature', 'Fighting a monster bare-handed')
def test_bare_handed_combat():
    pass


@scenario('features/combat.feature', 'Fighting a monster using gear')
def test_gear_combat():
    pass
