import ChessEngine
import math
import numpy as np
import copy

def print_board(board):
    for row in board:
        print(' '.join(row))
    print()

class Node:
    def __init__(self, gamestate, args, parent=None, action_taken=None):
        
        self.gamestate = gamestate
        self.args = args
        # self.state = state
        self.parent = parent
        self.action_taken = action_taken

        self.children = []
        self.expandable_moves = copy.deepcopy(self.gamestate.getValidMoves())
        # self.expandable_moves = self.gamestate.getValidMoves().copy()

        self.visit_counts = 0
        self.value_sum = 0
    def print_tree(self, depth=0):
        prefix = "  " * depth
        move_str = self.action_taken.getChessNotation() if self.action_taken else "ROOT"
        print(f"{prefix}{move_str} (Visits: {self.visit_counts}, Value: {self.value_sum})")
        for child in self.children:
            child.print_tree(depth + 1)

    def is_fully_expanded(self):
        return len(self.expandable_moves) == 0 and len(self.children) > 0
    
    def select(self):
        best_child = None
        best_ucb = -np.inf

        for child in self.children:
            ucb = self.get_ucb(child)
            if ucb > best_ucb:
                best_ucb = ucb
                best_child = child
                best_ucb = ucb
        return best_child
    
    def get_ucb(self, child):
        q_value = 1 - ((child.value_sum / child.visit_counts) + 1) / 2
    
        return  q_value + self.args['C'] * math.sqrt(math.log(self.visit_counts) / child.visit_counts)
    
    def expand(self):
        idx = np.random.randint(len(self.expandable_moves))
        action = self.expandable_moves.pop(idx)

        # child_gamestate = self.gamestate.copy()
        child_gamestate = copy.deepcopy(self.gamestate)
        child_gamestate.makeMove(action)
        child = Node(child_gamestate, self.args, parent=self, action_taken=action)
        self.children.append(child)
        return child
    
    def simulate(self):
        # value, is_terminal = self.gamestate.getValueAndTerminated()
        # value = self.gamestate.getOpponentValue(value)
        # if is_terminal:
        #     return value
        
        # rollout_gamestate = self.gamestate.copy()
        rollout_gamestate = copy.deepcopy(self.gamestate)
        rollout_player = rollout_gamestate.whiteToMove
        action_count = 0
        print_board(rollout_gamestate.board)
        while True:
            action_count+=1
            valid_moves = rollout_gamestate.getValidMoves()
            print('Rollout Valid Moves', valid_moves)
            value, is_terminal = rollout_gamestate.getValueAndTerminated()
            if value ==1:
                print("Rollout Value 1 Reached")
            
            if is_terminal:
                if rollout_gamestate.whiteToMove == rollout_player:
                    return rollout_gamestate.getOpponentValue(value)
                return value
            
            action = valid_moves[np.random.randint(len(valid_moves))]
            print("Rollout action:", action.getChessNotation())
            print("Action Count:", action_count)
            print(rollout_gamestate.drawMoveCounter)
            rollout_gamestate.makeMove(action)
            print_board(rollout_gamestate.board)
            
    
    def backpropagate(self, value):
        self.visit_counts += 1
        self.value_sum += value

        value = self.gamestate.getOpponentValue(value)
        if self.parent is not None:
            self.parent.backpropagate(value)


class MCTS:
    def __init__(self, gamestate, args):
        self.gamestate = gamestate
        self.args = args

    def search(self):
        # define root
        root = Node(self.gamestate, self.args)
        # selection
        for search in range(self.args['num_searches']):
            node = root
            while node.is_fully_expanded():
                node = node.select()
            
            # valid_moves = node.gamestate.getValidMoves()
            value, is_terminal = node.gamestate.getValueAndTerminated()
            value = node.gamestate.getOpponentValue(value)
            
            if not is_terminal:

                # expansion
                print(search)
                node = node.expand()
                
                # simulation
                value = node.simulate()

            # backpropagation
            node.backpropagate(value)
        
        possible_actions = []
        action_probs = []
        # return visit counts
        for child in root.children:
            action_probs.append(child.visit_counts)
            possible_actions.append(child.action_taken)
        
        action_probs = action_probs / np.sum(action_probs)
        root.print_tree()
        print('N Searches Really = ', search)
        print('N Searches = ', self.args['num_searches'])
        return possible_actions, action_probs