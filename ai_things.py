import random
from classes import Tetris
from copy import deepcopy
from numpy import average


normal_amount = 100
mutated_amount = 10
invasive_amount = 10
num_competitors = normal_amount+mutated_amount+invasive_amount
num_moves = 200
num_weights = 3


class bot:
    def __init__(self, weights):
        pass


class Competitor:
    def __init__(self, name, parent1=None, parent2=None):
        self.name = name
        self.weights = []
        self.super_score = 0
        # First generation
        if not parent1 and not parent2:
            self.weights = [random.uniform(0, 1) for i in range(num_weights)]
        # Proceeding generations inherit their parents characteristics randomly
        else:
            # Random cross breed
            for i in range(num_weights):
                if random.getrandbits(1):
                    self.weights.append(parent1.weights[i])
                else:
                    self.weights.append(parent2.weights[i])
        self.gamestate = Tetris()  # A new Tetris object

    def play(self):
        """
        Will play num_moves amount of moves or until death
        """
        for move in range(num_moves):
            if not self.gamestate.alive:
                print(f"Competitor {self.name} died prematurely")
                break
            best_move = self.optimal_move()
            # if move % 50 == 0:
                # print(f"Turn: {move}, {best_move}")
            self.gamestate.make_move(best_move)
        self.super_score = self.gamestate.score*0.2 if not self.gamestate.alive else self.gamestate.score
        print(f"Score: {self.super_score}\n\n")

        

    def calc_score(self, test_board):
        """
        How much does the move score based off the competitors weights?
        """
        score = 0
        score -= self.weights[0] * test_board.holes  # more holes worse
        score -= self.weights[1] * test_board.height_diff  # more height diff worse
        score += self.weights[2] * test_board.row_score  # more row_score better
        return score

    def deeper_optimal_score(self, deeper_board):
        """
        Returns move of form (rotation, side) optimised based off weights (calling calc_score)
        """
        best_score = float("-inf")
        for rotation in range(4):
            for horizontal in range(-5, 5):  # TODO: figure out horizontal range
                move = (rotation, horizontal)
                test_board = deepcopy(deeper_board)
                test_board.make_move(move)
                test_score = self.calc_score(test_board)
                if test_score > best_score:
                    best_score = test_score
        return best_score

    def optimal_move(self):
        best_score = float("-inf")
        best_move = None
        for rotation in range(4):
            for horizontal in range(-5, 5):  # TODO: figure out horizontal range
                #Make first move
                move = (rotation, horizontal)
                test_board = deepcopy(self.gamestate)
                test_board.make_move(move)
                #Add optimal second move
                test_score = self.calc_score(test_board)#+self.deeper_optimal_score(test_board)
                if test_score > best_score:
                    best_score = test_score
                    best_move = move
        return best_move

    def mutate(self):
        for weight in self.weights:
            if not random.getrandbits(2):
                weight = random.uniform(0, 1)

    def __str__(self):
        return f"Competitor: {self.name}\nHoles: {self.weights[0]}, Height difference: {self.weights[1]}, Line clearing: {self.weights[2]}"
    def __repr__(self):
        return f"Competitor: {self.name}\nHoles: {self.weights[0]}, Height difference: {self.weights[1]}, Line clearing: {self.weights[2]}\n\n"

class Generation:
    """
    Zeroeth generation begins with randomly weighted competitors
    When a new generation is made it takes in a parent generation's children and gen number
    """

    def __init__(self, parent_gen=None):
        self.parent_gen = parent_gen
        self.competitors = []
        self.children = []
        self.stats = {}
        self.comparison = {}
        # If there is a parent generation inherit the children
        if parent_gen:
            self.competitors = parent_gen.children
            self.gen_number = parent_gen.gen_number + 1
        # First generation completely random num_comp competitors
        else:
            names = iter(range(num_competitors))
            for i in range(num_competitors):
                name = next(names)
                zeros = (3 - len(str(name))) * "0"
                self.competitors.append(Competitor(f"0.{zeros}{name}"))
            self.gen_number = 0
        print(f"Generation {self.gen_number} created!\n")

    def train(self):
        print("Training...\n")
        for competitor in self.competitors:
            print(competitor)
            competitor.play()
        scores = [comp.super_score for comp in self.competitors]
        self.stats["avg"] = average(scores)
        self.stats["max"] = max(scores)
        self.stats["min"] = min(scores)
        if self.parent_gen:
            growth = {
                "avg": self.stats["avg"] - self.parent_gen.stats["avg"],
                "max": self.stats["max"] - self.parent_gen.stats["max"],
                "min": self.stats["min"] - self.parent_gen.stats["min"],
            }
            print(
                f"Generation {self.gen_number}\nStats: {self.stats}\nGrowth: {growth}"
            )
        else:
            print(f"Generation {self.gen_number}\nStats: {self.stats}")
        self.breed()

    def breed(self):
        print("Breeding...\n\n")
        names = iter(range(num_competitors))
        # natural selection (Keep top 25%)
        viable_parents = sorted(
            self.competitors, key=lambda x: x.super_score, reverse=True
        )[: len(self.competitors) // 4]
        for i in range(normal_amount):
            name = next(names)
            zeros = (3 - len(str(name))) * "0"
            self.children.append(
                Competitor(
                    f"{self.gen_number+1}.{zeros}{name}",
                    random.choice(viable_parents),
                    random.choice(viable_parents),
                )
            )
        # mutate some of the children
        for i in range(mutated_amount):
            name = next(names)
            zeros = (3 - len(str(name))) * "0"
            child = Competitor(
                f"{self.gen_number+1}.{zeros}{name}",
                random.choice(viable_parents),
                random.choice(viable_parents),
            )
            child.mutate()
            self.children.append(child)

        #Invasive
        for i in range(invasive_amount):
            name = next(names)
            zeros = (3 - len(str(name))) * "0"
            child = Competitor(f"{self.gen_number+1}.{zeros}{name}")     
            self.children.append(child)
        


# Bumpiness of the board (more bumpy probably worse?? might depend on the piece)

# Number of holes created (more is worse) a hole could be an open hole would still be bad, deepness of hole

# Difference in height (greater is worse) (might be similar to height)

# Split path, next piece vs current piece

#look into future(consider upcoming piece)

#homogeneity of a generation, invasive species?

#Making long holes things is bad if its not for tetris set up

#Tetris potential