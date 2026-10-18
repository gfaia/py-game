from entities import Mechanic, Player, Sentinel
from map_data import MAP_ROWS, MECHANIC_START, PLAYER_START, SENTINEL_START
from settings import ENEMY_COLOR, NPC_COLOR, PLAYER_COLOR


class World:
    def __init__(self):
        self.reset()

    def reset(self):
        self.map_rows = MAP_ROWS
        self.player = Player("Explorer", PLAYER_START, PLAYER_COLOR)
        self.mechanic = Mechanic("Mechanic Ada", MECHANIC_START, NPC_COLOR)
        self.sentinel = Sentinel("Clockwork Sentinel", SENTINEL_START, ENEMY_COLOR)
        self.quest_state = "not_started"
        self.message = "Find Mechanic Ada near the brass pipe."
        self.game_over = False

    def terrain_at(self, position):
        column, row = position
        if row < 0 or row >= len(self.map_rows):
            return None
        if column < 0 or column >= len(self.map_rows[row]):
            return None
        return self.map_rows[row][column]

    def is_walkable(self, position):
        return self.terrain_at(position) in {".", "=", "B"}

    def is_adjacent(self, first, second):
        return abs(first[0] - second[0]) + abs(first[1] - second[1]) == 1

    def occupant_at(self, position):
        if self.mechanic.position == position:
            return self.mechanic
        if self.sentinel.alive and self.sentinel.position == position:
            return self.sentinel
        return None

    def move_player(self, delta):
        if self.game_over:
            self.message = "Press R to begin a new expedition."
            return False
        target = (self.player.position[0] + delta[0], self.player.position[1] + delta[1])
        if not self.is_walkable(target):
            self.message = "Steam pipes block that route."
            return False
        if self.occupant_at(target):
            self.message = "That space is occupied."
            return False
        self.player.position = target
        self.message = "The station gears creak under your boots."
        return True

    def interact(self):
        if self.game_over:
            self.message = "Press R to begin a new expedition."
            return
        if not self.is_adjacent(self.player.position, self.mechanic.position):
            self.message = "Stand beside Mechanic Ada to talk."
            return
        if self.quest_state == "not_started":
            self.quest_state = "active"
            self.message = "Ada: Destroy the lost clockwork sentinel."
        elif self.quest_state == "active":
            self.message = "Ada: The sentinel still blocks the lower platform."
        else:
            self.message = "Ada: The station breathes again. Task complete."

    def attack_enemy(self):
        if self.game_over:
            self.message = "Press R to begin a new expedition."
            return
        if not self.sentinel.alive or not self.is_adjacent(self.player.position, self.sentinel.position):
            self.message = "Stand beside the sentinel to attack."
            return
        self.sentinel.health -= self.player.attack
        if not self.sentinel.alive:
            self.sentinel.health = 0
            self.quest_state = "ready_to_turn_in"
            self.message = "The sentinel stops. Return to Ada."
            return
        self.player.health -= self.sentinel.attack
        if self.player.health <= 0:
            self.player.health = 0
            self.game_over = True
            self.message = "The sentinel overpowers you. Press R to restart."
            return
        self.message = "You strike the sentinel. It returns fire."

    def quest_label(self):
        labels = {
            "not_started": "Task: Speak with Ada",
            "active": "Task: Disable the sentinel",
            "ready_to_turn_in": "Task: Report to Ada",
        }
        return labels[self.quest_state]
