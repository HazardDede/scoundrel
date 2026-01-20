Feature: Combat
  As a player
  I want to fight monsters
  So that I can clear the room and survive

  Scenario: Fighting a monster bare-handed
    Given a player with 20 health
    And the room containing a "Skeleton" monster of rank 9
    And the room containing a "Goblin" monster of rank 5
    When the player attacks the "Skeleton" bare-handed
    Then the player should have 11 health remaining
    And the "Skeleton" should be removed from the room
    And the "Goblin" should still be in the room
    When the player attacks the "Goblin" bare-handed
    Then the player should have 6 health remaining
    And the "Goblin" should be removed from the room

  Scenario: Fighting a monster using gear
    Given a player with 20 health
    And an equipped weapon called "Sword" of rank 5
    And the room containing a "Skeleton" monster of rank 9
    And the room containing a "Goblin" monster of rank 5
    And the room containing a "Dragon" monster of rank 14
    When the player attacks the "Skeleton" using his gear
    Then the player should have 16 health remaining
    And the "Skeleton" should be removed from the room
    And the "Goblin" should still be in the room
    And the "Dragon" should still be in the room
    And the weapons last slain monster should be a "Skeleton" of rank 9
    When the player attacks the "Goblin" using his gear
    Then the player should have 16 health remaining
    And the "Goblin" should be removed from the room
    And the "Dragon" should still be in the room
    And the "Dragon" cannot be attacked using the gear
    And the weapons last slain monster should be a "Goblin" of rank 5
