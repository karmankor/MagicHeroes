class Weapon:
    def __init__(self, name, life, repair_cost, effects):
        self.name = name
        self.max_life = life
        self.current_life = life
        self.repair_cost = repair_cost
        self.effects = effects

    def reset(self):
        self.current_life = self.max_life
