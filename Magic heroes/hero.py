class Hero:
    def __init__(self, name, life, description, bonuses):
        self.name = name
        self.max_life = life
        self.current_life = life
        self.mana = 0
        self.shield = 0
        self.description = description
        self.bonuses = bonuses
    def reset(self):
        self.current_life = self.max_life
