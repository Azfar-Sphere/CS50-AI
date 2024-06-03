"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O" 
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    if terminal(board):
        return 3

    num_X = 0
    num_O = 0

    for row in board:
        for cell in row:
            if cell == X:
                num_X += 1
            if cell == O:
                num_O += 1

    if num_X == 0 and num_O == 0:
        return X
    if num_X > num_O:
        return O
    elif num_X == num_O:
        return X
    
        
def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    if terminal(board):
        return 3
    
    actions_set = set()

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                actions_set.add((i, j))
    
    return actions_set


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action is None:
        return board

    new_board = copy.deepcopy(board)

    if board[action[0]][action[1]] != EMPTY:
        raise Exception("Invalid Action")
    
    if not 0 <= action[0] < 3:
        raise Exception("Invalid Action")
    
    if not 0 <= action[1] < 3:
        raise Exception("Invalid Action")

    new_board[action[0]][action[1]] = player(board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Checks Horizontally for winners

    for row in board:
        X_count = 0
        O_count = 0

        for cell in row:
            if cell == X:
                X_count += 1
            elif cell == O:
                O_count += 1

        if X_count == 3:
            return X
        elif O_count == 3:
            return O
        
    # Checks Vertically
    for j in range(3):
        column_list = []
        X_count = 0
        O_count = 0

        for i in range(3):
            if board[i][j] == X:
                X_count += 1
            if board[i][j] == O:
                O_count += 1

        if X_count == 3:
            return X
        elif O_count == 3:
            return O
        
    # Checks Diagonally Right to left
    X_count = 0
    O_count = 0
    for i in range(3):
  
        if board[i][i] == X:
            X_count += 1
        if board[i][i] == O:
            O_count += 1

    if X_count == 3:
        return X
    elif O_count == 3:
        return O
        
    # Checks Diagonally Left to Right
    X_count = 0
    O_count = 0
    for i in range(3):

        if board[i][2-i] == X:
            X_count += 1
        if board[i][2-i] == O:
            O_count += 1
            
    if X_count == 3:
        return X
    elif O_count == 3:
        return O
        
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return True

    count_cells = 0

    for row in board:
        for cell in row:
            if cell:
                count_cells += 1
    
    if count_cells == 9:
        return True
    
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)

    match win:
        case "X": 
            return 1
        case "O":
            return -1
        case None:
            return 0
        case _: 
            return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    current_player = player(board)

    if current_player == X:
        best_value = -999
        best_action = None
        for action in actions(board):
            value = min_value(result(board, action))
            if value > best_value:
                best_value = value
                best_action = action

        return best_action
    
    if current_player == O:
        best_value = 999
        best_action = None
        for action in actions(board):
            value = max_value(result(board, action))
            if value < best_value:
                best_value = value
                best_action = action

        return best_action


def max_value(board):
    v = -999
    if terminal(board):
        return utility(board)
    
    for action in actions(board):
        v = max(v, min_value(result(board, action)))

    return v
    

def min_value(board):
    v = 999
    if terminal(board):
        return utility(board)
    
    for action in actions(board):
        v = min(v, max_value(result(board, action)))

    return v