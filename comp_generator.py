import time
import json
import copy

class CompGenerator:
    def __init__(self, game):
        self.allHeros = []
        self.allSynergies = []
        self.bestComps = TeamCompList()
        self.initialize_json_heros()
        self.initialize_json_synergies()
        self.game = game

    def initialize_json_heros(self):
        with open('heros.json') as json_file:
            self.allHeros = json.load(json_file)
            # for hero in heros:
            #     classes = heros[hero]['classes']
            #     origins = heros[hero]['origins']
            #     self.allHeros.append(Hero(hero, classes, origins))

    def initialize_json_synergies(self):
        with open('synergies.json') as json_file:
            self.allSynergies = json.load(json_file)
            # temp = self.allSynergies['class']['Assassin']['breakpoint']
            # print(temp)
            # print(temp.pop())
            # print(temp.pop())


    def print_all_heros(self):
        for hero in self.allHeros:
            print(hero.name, hero.classes, hero.origins)
    
    def calculate_distance(self, hero1, hero2):
        if hero1 == hero2:
            return 0
        if self.have_synergy(hero1, hero2):
            return 1
        for c in self.get_classes(hero2):
            for h in self.get_heros_of_classes(c):
                if self.have_synergy(hero1, h):
                    return 2
        for o in self.get_origins(hero2):
            for h in self.get_heros_of_origins(o):
                if self.have_synergy(hero1, h):
                    return 2
        else:
            return 3
        
    def have_synergy(self, hero1, hero2):
        return self.do_share_class(hero1, hero2) or self.do_share_origin(hero1, hero2)

    def do_share_class(self, hero1, hero2):
        for c in self.get_classes(hero1):
            if c in self.get_classes(hero2):
                return True
        return False

    def do_share_origin(self, hero1, hero2):
        for o in self.get_origins(hero1):
            if o in self.get_origins(hero2):
                return True
        return False

    def get_classes(self, hero):
        return self.allHeros[hero]['classes']

    def get_origins(self, hero):
        return self.allHeros[hero]['origins']
    
    def get_cost(self, hero):
        return self.allHeros[hero]['cost']

    def get_costs_of_comp(self, tc):
        costs = list()
        for h in tc.get_heros():
            costs.append(self.allHeros[h]['cost'])
        return costs

    def get_heros_of_classes(self, cls):
        heros = list()
        if isinstance(cls, str):
            cls = [cls]
        for c in cls:
            for hero in self.allHeros:
                if c in self.get_classes(hero):
                    if hero not in heros:
                        heros.append(hero)
        return heros

    def get_heros_of_origins(self, org):
        heros = list()
        if isinstance(org, str):
            org = [org]
        for o in org:
            for hero in self.allHeros:
                if o in self.get_origins(hero):
                    if hero not in heros:
                        heros.append(hero)
        return heros

    def get_heros_with_synergy(self, hero):
        hero_list = list()
        for h in self.allHeros:
            if self.have_synergy(h, hero) and h != hero:
                hero_list.append(h)

        return hero_list

    def generate_tree(self, hero_root, max_cost, depth, team_comp):
        if isinstance(hero_root, str):
            hero_root = [hero_root]
        
        depth = depth - len(hero_root) + 1
        for h in hero_root:
            team_comp.add_hero(h)
            for c in self.get_classes(h):
                team_comp.increase_class_score(c)
            for o in self.get_origins(h):
                team_comp.increase_origin_score(o)

        # hero_root = hero_root[0]

        for hr in hero_root:
        
            if depth == 1:
                score = self.calculate_cumulative_distance(team_comp)
                team_comp.set_score(score)
                # if team_comp.get_heros() == ['Varus', 'Ashe', 'Braum', 'Leona']:
                #     print('hi')
                total_synergy = self.calculate_synergy_score(team_comp)
                team_comp.set_total_synergy(total_synergy)
                self.bestComps.add_team_comp(team_comp)

            else:
                for h in self.get_heros_with_synergy(hr):
                    if self.get_cost(h) <= max_cost:
                        # print(self.get_cost(h))
                        if not team_comp.has_hero(h):
                            self.generate_tree(h, max_cost, depth - 1, copy.deepcopy(team_comp))
            
        
    def generate_best_comps(self, hero_root, max_cost, depth):
        self.bestComps = TeamCompList()
        team_comp = TeamComp(self.game)
        self.generate_tree(hero_root, max_cost, depth, team_comp)

    def print_best_comps(self, num):
        self.bestComps.sort_list()
        bc = self.bestComps.get_comp_list()
        if num > len(bc):
            num = len(bc)
        # for c in self.bestComps:
        for i in range(num):
            c = bc[i]
            print(c.get_heros(), c.get_total_synergy(), self.get_costs_of_comp(c))
            # print(len(c.get_heros()))
            # for h in c.get_heros():
            #     print(h, self.get_classes(h), self.get_origins(h))
        print(len(bc))

    def get_best_comps(self):
        self.bestComps.sort_list()
        return self.bestComps

    def existing_best_comp(self, comp):
        for bc in self.bestComps:
            if len(bc) != len(comp):
                continue
            if bc.sort() == comp.sort():
                return 1
        return 0

    def calculate_cumulative_distance(self, tc):
        score = 0
        num_terms = 0
        for h1 in tc.get_heros():
            for h2 in tc.get_heros():
                dist = self.calculate_distance(h1, h2)
                if dist:
                    score += dist
                    num_terms += 1
        return score / num_terms

    def calculate_synergy_score(self, tc):
        synergy_score = 0
        ss = tc.get_synergy_scores()
        for c in ss['class']:
            score = ss['class'][c]
            if score == 0:
                continue
            bp = copy.copy(self.allSynergies['class'][c]['breakpoint'])
            while bp:
                val = bp.pop()
                if score >= val:
                    synergy_score += val
                    # print(c)
                    break
        
        for o in ss['origin']:
            score = ss['origin'][o]
            if score == 0:
                continue
            bp = copy.copy(self.allSynergies['origin'][o]['breakpoint'])
            while bp:
                val = bp.pop()
                if score >= val:
                    synergy_score += val
                    # print(o)
                    break

        return synergy_score

    def create_team_comp(self, tc_list):
        tc = TeamComp(self.game)
        for h in tc_list:
            tc.add_hero(h)
            for c in self.get_classes(h):
                tc.increase_class_score(c)
            for o in self.get_origins(h):
                tc.increase_origin_score(o)

        score = self.calculate_cumulative_distance(tc)
        tc.set_score(score)
        total_synergy = self.calculate_synergy_score(tc)
        tc.set_total_synergy(total_synergy)
        
        return tc


class TeamCompList:
    def __init__(self, all_heros = []):
        self.teamCompList = list()
        self.allHeros = all_heros
    
    def add_team_comp(self, tc):
        if not self.already_in_list(tc):
            self.teamCompList.append(tc)

    def already_in_list(self, new_tc):
        for tc in self.teamCompList:
            t1 = tc.get_heros()
            t1.sort()
            t2 = new_tc.get_heros()
            t2.sort()
            if t1 == t2:
                return 1
        return 0

    def get_comp_list(self):
        return self.teamCompList

    def sort_list(self):
        self.teamCompList = sorted(self.teamCompList, key=lambda team: team.get_total_synergy(), reverse=True)

class TeamComp:
    def __init__(self, game):
        self.heros = []
        self.score = []
        self.total_synergy = 0
        if game == 'tft':
            self.synergy_scores = {
                "class": {
                    "Assassin": 0,
                    "Blademaster": 0,
                    "Brawler": 0,
                    "Elementalist": 0,
                    "Guardian": 0,
                    "Gunslinger": 0,
                    "Knight": 0,
                    "Ranger": 0,
                    "Shapeshifter": 0,
                    "Sorcerer": 0   
                },
                "origin": {
                    "Demon": 0,
                    "Dragon": 0,
                    "Exile": 0,
                    "Glacial": 0,
                    "Imperial": 0,
                    "Noble": 0,
                    "Ninja": 0,
                    "Pirate": 0,
                    "Phantom": 0,
                    "Robot": 0,
                    "Void": 0,
                    "Wild": 0,
                    "Yordle": 0
                }
            }
        else:
            self.synergy_scores = {
                "class": {
                    "Assassin": 0,
                    "Elusive": 0,
                    "Demon": 0,
                    "Demon Hunter": 0,
                    "Human": 0,
                    "Savage": 0,
                    "Scaled": 0,
                    "Troll": 0,
                    "Warlock": 0,
                    "Brawny": 0,
                    "Deadeye": 0,
                    "Druid": 0,
                    "Heartless": 0,
                    "Hunter": 0,
                    "Knight": 0,
                    "Mage": 0,
                    "Dragon": 0,
                    "Inventor": 0,
                    "Primordial": 0,
                    "Shaman": 0,
                    "Blood-Bound": 0,
                    "Warrior": 0,
                    "Scrappy": 0
                 },
                "origin": {
                }
            }
            

    def add_hero(self, hero):
        if hero not in self.heros:
            self.heros.append(hero)
            return 1
        else:
            return 0

    def set_total_synergy(self, score):
        self.total_synergy = score

    def get_total_synergy(self):
        return self.total_synergy
        
    def increase_class_score(self, c):
        self.synergy_scores['class'][c] += 1
        return self.synergy_scores['class'][c]

    def increase_origin_score(self, o):
        self.synergy_scores['origin'][o] += 1
        return self.synergy_scores['origin'][o]

    def get_synergy_scores(self):
        return self.synergy_scores

    def remove_hero(self, hero):
        self.heros.remove(hero)

    def set_score(self, score):
        self.score = score
    
    def get_score(self):
        return self.score

    def get_heros(self):
        return self.heros

    def has_hero(self, hero):
        return hero in self.heros
    

if __name__ == "__main__":
    start = time.time()
    cg = CompGenerator('dota')
    # tc = cg.create_team_comp(['Aatrox', 'Brand', 'Elise', 'Nidalee', 'Swain', 'Warwick'])
    # print(tc.get_total_synergy())
    # cg.generate_tree(["Kha'Zix", 'Ashe', 'Vayne', 'Varus', 'Mordekaiser'], 9, TeamComp())
    # cg.print_best_comps(20)
    print(time.time() - start)
