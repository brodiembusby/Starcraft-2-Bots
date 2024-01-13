from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units


class TerranSetupBot(BotAI):
    async def on_step(self, iteration: int):
        
        ccs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
        #First Command Center
        cc: Unit = ccs.first

        # If command center can afford scv then train them
        if self.can_afford(UnitTypeId.SCV) and cc.is_idle and ccs.first.surplus_harvesters != 18:
            cc.train(UnitTypeId.SCV)
        
        # If the supply is almost capped then build only two more at a time
        if self.can_afford(UnitTypeId.SUPPLYDEPOT) and self.supply_left < 2  and self.already_pending(UnitTypeId.SUPPLYDEPOT) < 2:
            await self.build(UnitTypeId.SUPPLYDEPOT,near=cc.position.towards(self.game_info.map_center,5))
        
        # Build 3 Barracks near the CC
        elif self.can_afford(UnitTypeId.BARRACKS) and self.structures(UnitTypeId.BARRACKS).amount != 3:
            await self.build(UnitTypeId.BARRACKS,near=cc.position.towards(self.game_info.map_center,5))
        
        # For all Barracks build marines
        for rax in self.structures(UnitTypeId.BARRACKS).ready.idle:
            rax.train(UnitTypeId.MARINE)
        
        # Instantaite marines into a group
        marines: Units = self.units(UnitTypeId.MARINE).idle
        # If there are more than 15 marines attack the enemy base
        if marines.amount > 15:
            target: Point2 = self.enemy_structures.random_or(self.enemy_start_locations[0]).position
            for marine in marines:
                marine.attack(target)
        # Make idle workers harvest minerals   
        for scv in self.workers.idle:
            scv.gather(self.mineral_field.closest_to(cc))
# Run the game on AbyssalReef out bot is Terran, The normal computer is Protoss and medium difficulty.
run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Terran, TerranSetupBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=False)