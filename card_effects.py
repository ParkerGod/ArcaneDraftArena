class BaseEffect:
    def execute(self, battle, caster, target, card):
        pass


class FireEffect(BaseEffect):
    def execute(self, battle, caster, target, card):
        damage = card.damage
        if battle.defending_card:
            from models import calculate_damage
            damage = calculate_damage(card, battle.defending_card)
        target.take_damage(damage)
        battle.log.append(f"{caster.name} 使用 {card.name}，造成 {damage} 点伤害！")


class WaterEffect(BaseEffect):
    def execute(self, battle, caster, target, card):
        from models import calculate_damage
        damage = calculate_damage(card, battle.defending_card) if battle.defending_card else card.damage
        target.take_damage(damage)
        heal = 2
        caster.hp = min(caster.max_hp, caster.hp + heal)
        battle.log.append(f"{caster.name} 使用 {card.name}，造成 {damage} 点伤害，恢复 {heal} 点生命！")


class WindEffect(BaseEffect):
    def execute(self, battle, caster, target, card):
        from models import calculate_damage
        damage = calculate_damage(card, battle.defending_card) if battle.defending_card else card.damage
        target.take_damage(damage)
        if len(caster.hand) < 7 and caster.deck:
            caster.draw_card(1)
            battle.log.append(f"{caster.name} 使用 {card.name}，造成 {damage} 点伤害，抽1张牌！")
        else:
            battle.log.append(f"{caster.name} 使用 {card.name}，造成 {damage} 点伤害！")
