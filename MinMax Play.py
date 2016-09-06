""" 6.034 Lab 6 2015: Neural Nets & SVMs
 Designed and implemented by Rafal Jankowski, Oct 2015
 To play use board examples from boards.py and evaluate individual function, for example:
 endgame_score_connectfour(BOARD_FULL_TIED_minus3, 1)
 Or evaluate using one of the optimising algorithms, for example:
 pretty_print_dfs_type(minimax_search(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=3))
 """


from game_api import *
from boards import *
INF = float('inf')

def is_game_over_connectfour(board) :
    if board.count_pieces() >= board.num_rows * board.num_cols:
        return True
    for i in board.get_all_chains():
        if len(i) >= 4:
            return True
    return False

def next_boards_connectfour(board):
    all_moves = []
    if is_game_over_connectfour(board):
        return []
    else:
        for i in range(board.num_cols):
            if board.get_column_height(i) < board.num_rows:
                all_moves.append(board.add_piece(i))
    return all_moves

def endgame_score_connectfour_faster(board, is_current_player_maximizer) :
    max_pieces  = board.num_rows * board.num_cols
    if is_game_over_connectfour(board):
        for i in board.get_all_chains():
            if len(i) >= 4:
                if is_current_player_maximizer:
                    return -1000 - (max_pieces-board.count_pieces())
                else:
                    return 1000 + (max_pieces-board.count_pieces())
        return 0
    return 0

def endgame_score_connectfour(board, is_current_player_maximizer) :
    """Given an endgame board, returns an endgame score with abs(score) >= 1000,
    returning larger absolute scores for winning sooner."""
    if is_game_over_connectfour(board):
        if is_current_player_maximizer:
            return -1000
        else:
            return 1000
    return 0

def endgame_score_connectfour(board, is_current_player_maximizer) :
    if is_game_over_connectfour(board):
        for i in board.get_all_chains():
            if len(i) >= 4:
                if is_current_player_maximizer:
                    return -1000
                else:
                    return 1000
        return 0
    return 0

# ------------------ Attempt 1 using a heuristic ----------------
def heuristic_connectfour(board, is_current_player_maximizer) :
    """Given a non-endgame board, returns a heuristic score with
    abs(score) < 1000, where higher numbers indicate that the board is better
    for the maximizer."""
    current_player = board.__piece_type__(board.get_current_player_name())
    
    if is_game_over_connectfour(board):
        for i in board.get_all_chains():
            if len(i) >= 4:
                if is_current_player_maximizer:
                    return -1000
                else:
                    return 1000
        return 0
    else:
        all_chains = board.get_all_chains()
        chain_val_curr = 0
        chain_val_oth = 0
        for i in all_chains:
            if i[0] == current_player:
                chain_val_curr += len(i)
            else:
                chain_val_oth += len(i)
        if is_current_player_maximizer:
        # max's turn
            # if max is winning
            if chain_val_curr > chain_val_oth:
                return 1000 - 200 + chain_val_oth
            else:
                return -1000 + chain_val_curr
        else:
            # if max is winning
            if chain_val_oth > chain_val_curr:
                return 1000 - 200 + chain_val_oth
            else:
                return -1000 + chain_val_curr

    return 0


# This AbstractGameState represents a new ConnectFourBoard, before the game has started:
state_starting_connectfour = AbstractGameState(snapshot = ConnectFourBoard(),
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "NEARLY_OVER" from boards.py:
state_NEARLY_OVER = AbstractGameState(snapshot = NEARLY_OVER,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "BOARD_UHOH" from boards.py:
state_UHOH = AbstractGameState(snapshot = BOARD_UHOH,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)


# ------------------ Attempt 2 using depth-first search --------------------
def dfs_maximizing(state) :
    """Performs depth-first search to find path with highest endgame score."""
    snapshot = state.snapshot
    is_game_over_fn = state.is_game_over_fn
    generate_next_states_fn = state.generate_next_states_fn
    endgame_score_fn = state.endgame_score_fn
    
    best_score = -9999999
    best_path = []
    score_evals = 0
    
    stack = [(snapshot, [snapshot])]

    while stack:
        (vertex, path) = stack.pop()
        for next in generate_next_states_fn(vertex):
            path_abstract = []
            if is_game_over_fn(next):
                
                for i in path + [next]:
                    path_abstract.append(AbstractGameState(snapshot = i,
                                                             is_game_over_fn = is_game_over_connectfour,
                                                             generate_next_states_fn = next_boards_connectfour,
                                                             endgame_score_fn = endgame_score_connectfour_faster))
                score_evals += 1
                score = endgame_score_fn(next, 1)
                if score > best_score:
                    best_score = score
                    best_path = path_abstract
            else:
                stack.append((next, path + [next]))
    return (best_path, best_score, score_evals)

#print dfs_maximizing(state_NEARLY_OVER)


# -------------------------------- 3 Implementing MinMax algorithm --------------------------------------------
#Helper function for implementing the MinMax optimization at the bottom
def minimax_help(state, maximize, best_path, score_evals):
    best_score_eval = None
    if maximize == True:
        maxmin = 1
    else:
        maxmin = 0
    snapshot = state.snapshot
    is_game_over_fn = state.is_game_over_fn
    generate_next_states_fn = state.generate_next_states_fn
    endgame_score_fn = state.endgame_score_fn

    if is_game_over_fn(snapshot):
        return (best_path, endgame_score_fn(snapshot, maxmin), score_evals)
    else:
        lista = []
        for next in generate_next_states_fn(snapshot):
            next_state = AbstractGameState(snapshot = next,
                                           is_game_over_fn = is_game_over_connectfour,
                                           generate_next_states_fn = next_boards_connectfour,
                                           endgame_score_fn = endgame_score_connectfour_faster)
            lista.append(next_state)
        if maximize == True:
            best_score_eval = max([minimax_help(i, False, best_path + [i], score_evals + 1) for i in lista])
        else:
            best_score_eval = min([minimax_help(i, True, best_path + [i], score_evals + 1) for i in lista])
                             
    return best_score_eval #(best_path, best_score_eval, score_evals)

def minimax_endgame_search(state, maximize=True):
    best_path = [state]
    score_evals = 0
    return minimax_help(state, True, best_path, score_evals)

#pretty_print_dfs_type(minimax_endgame_search(state_NEARLY_OVER))
#pretty_print_dfs_type(dfs_maximizing(state_NEARLY_OVER))


# Second helper function
def minimax_help2(state, maximize, best_path, score_evals, depth, heuristic_fn):
    best_score_eval = None
    if maximize == True:
        maxmin = 1
    else:
        maxmin = 0
    
    snapshot = state.snapshot
    is_game_over_fn = state.is_game_over_fn
    generate_next_states_fn = state.generate_next_states_fn
    endgame_score_fn = state.endgame_score_fn

    if is_game_over_fn(snapshot):
        return (best_path, endgame_score_fn(snapshot, maxmin), score_evals)
    
    elif depth <= 0:
        return (best_path, heuristic_fn(snapshot, maxmin), score_evals)
    else:
        lista = []
        for next in generate_next_states_fn(snapshot):
            next_state = AbstractGameState(snapshot = next,
                                           is_game_over_fn = is_game_over_connectfour,
                                           generate_next_states_fn = next_boards_connectfour,
                                           endgame_score_fn = endgame_score_connectfour_faster)
            lista.append(next_state)
        if maximize == True:
            best_score_eval = max([minimax_help2(i, False, best_path + [i], score_evals + 1, depth - 1, heuristic_fn) for i in lista])
        else:
            best_score_eval = min([minimax_help2(i, True, best_path + [i], score_evals + 1, depth - 1, heuristic_fn) for i in lista])

    return best_score_eval #(best_path, best_score_eval, score_evals)

# Using the helper functions - minimax search
def minimax_search(state, heuristic_fn=always_zero, depth_limit=INF, maximize=True) :
    "Performs standard minimax search.  Same return type as dfs_maximizing."
    best_path = [state]
    score_evals = 0
    return minimax_help2(state, maximize, best_path, score_evals, depth_limit, heuristic_fn)




# Uncomment the line below to try minimax_search with "BOARD_UHOH" and
# depth_limit=1.  Try increasing the value of depth_limit to see what happens:

pretty_print_dfs_type(minimax_search(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=3))



