import ChessEngine
import random
import numpy as np
import copy


pieceValues = {
    'p': 100,  # Pawn
    'R': 500,  # Rook
    'N': 300,  # Knight
    'B': 300,  # Bishop
    'Q': 900,  # Queen
    'K': 2000000,  # King (very high value to avoid losing it)
}

def evaluate_position(gs):
    whitePiecesVal = 0
    blackPiecesVal = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board)):
            piece = gs.board[row][col]
            if piece[0] == 'w':
                whitePiecesVal += pieceValues.get(piece[1], 0)
            elif piece[0] == 'b':
                blackPiecesVal += pieceValues.get(piece[1], 0)
    
    evaluation = whitePiecesVal - blackPiecesVal
    if not gs.whiteToMove:
        evaluation = -evaluation
    
    return evaluation

def build_move_tree(gs, depth, whitePlayer):
    """
    Build a tree of all possible move‐sequences up to `depth`.
    Each node is a dict:
      {
        "move":       move_obj,       # None for root
        "captured":   int,            # value of capture on this move
        "children":   [child_nodes...]
      }
    """
    root = {"move": None, "captured": 0, "children": []}
    _expand_node(gs, pieceValues, depth, root, whitePlayer)
    return root

def _expand_node(gs, pieceValues, depth, node, whitePlayer):
    if depth == 0:
        return
    for move in gs.getValidMoves():
        # captured_value = pieceValues.get(move.pieceCaptured[1], 0)
        # if (whitePlayer and not gs.whiteToMove) or (not whitePlayer and gs.whiteToMove):
        #     captured_value = -captured_value
        evaluation = evaluate_position(gs)
        gs.makeMove(move)
        # 3) create child node
        child = {
            "move":     move,
            "eval": evaluation,
            "children": []
        }
        node["children"].append(child)

        # 4) recurse one level deeper
        _expand_node(gs, pieceValues, depth - 1, child, whitePlayer)

        # 5) undo the move so we can try the next sibling
        gs.undoMove()

def find_max_capture_path(tree):
    """
    Returns (path, total_value), where path is list of move_objs
    that gives the maximum sum of captured values.
    """
    # Base: leaf
    if not tree["children"]:
        return [], 0

    best_sum = float("-inf")
    best_path = []

    for child in tree["children"]:
        # recurse into children
        subpath, subsum = find_max_capture_path(child)
        subsum += child["eval"]

        if subsum > best_sum:
            best_sum, best_path = subsum, [child["move"]] + subpath

    return best_path, best_sum

def findBestMove(gs, whitePlayer, depth):
    gs = copy.deepcopy(gs)
    tree = build_move_tree(gs, depth=depth, whitePlayer=whitePlayer)
    # print(tree)
    best_moves, best_value = find_max_capture_path(tree)
    if best_value == 0:
        return random.choice(best_moves)

    print(best_moves)
    print(best_value)
    return best_moves[0]

if __name__ == "__main__":
    gs = ChessEngine.GameState()
    print(evaluate_position(gs))
    gs.makeMove(gs.getValidMoves()[0])
    print(evaluate_position(gs))
# whitePlayer = True
# find_best_move(ChessEngine.GameState())

# ---------------------------
# Example usage:
#
# gs = YourGameState()
# pieceValues = {"p":1, "n":3, "b":3, "r":5, "q":9}
#
# tree = build_move_tree(gs, pieceValues, depth=3)
# best_moves, best_value = find_max_capture_path(tree)
#
# print("Best capture sequence:")
# for mv in best_moves:
#     print(mv)           # or mv.uci(), mv.san(), etc.
# print("Total captured value:", best_value)

        
# # Look all possible moves
# def get_captures(gs, valid_moves):
#     """
#     Get all capture moves from the list of valid moves.
#     """
#     captures = np.array([move for move in valid_moves if move.pieceCaptured != '--'])
#     print(captures)
#     if captures.size == 0:
#         print("No captures found", captures)
#         return None  # No captures available
    
#     values = np.array([pieceValues[move.pieceCaptured[1]] for move in captures])
#     max_val_move = captures[np.argmax(values)]
#     return max_val_move

# def get_random_move(valid_moves):
#     """
#     Return a random valid move.
#     """
#     return random.choice(valid_moves) if valid_moves else None

# def findBestMove(gs, valid_moves):
#     # look for captures and get highest value capture move
#     # return random.choice(valid_moves) if valid_moves else None
#     captures = get_captures(gs, valid_moves)
#     if captures is not None:
#         return captures
#     return get_random_move(valid_moves) if valid_moves else None



    