# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 14:42:53 2020

@author: Johannes
"""

import time
import numpy as np

class Game:
    
    def __init__(self):
        self.initialize_game()
        
    def inputNumber(self,prompt):
        while True:
            try:
                num = int(input(prompt))
                break
            except ValueError:
                print("\n-------------ERROR-----------------")
                print("\nPlease choose a valid number")
                print("\n------------------------------")
                pass
        return num
    
    def displayMenu(self,options, text):
        
        #Prints menu using the list 'options'
        for i in range(len(options)):
            print("{}. {}".format(i+1,options[i]))

        choice = 0
        
        #Handles input and displays error if choice is invalid
        while not choice in np.arange(1,len(options)+1):
            choice = self.inputNumber(text)
            if choice > len(options) or choice <= 0:
                print("\nInvalid choice")
    
        return choice
        
    def initialize_game(self):

        print("================ WELCOME TO THE KALAHA GAME ================")
        
        # Gets user input in order to initialize the game
        self.pocketnum = self.inputNumber("How many pockets should each player have? ")
        self.ballnum = self.inputNumber("How many balls in each pocket? ")
        self.depth = self.inputNumber("How deep should the AI search for a solution (more than 11 not recommended)? ")
       
        print()
        menu_choice = self.displayMenu(['Minimax','Alpha-beta w. evaluation function 1','Alpha-beta w. evaluation function 2','Alpha-beta w. evaluation function 3'],"Choose the AI algorithm to play with: ")        
        if menu_choice == 1:
            self.algo = "minimax"
        elif menu_choice == 2:
            self.algo = "ab"
        elif menu_choice == 3:
            self.algo = "ab_sumpockets"
        elif menu_choice == 4:
            self.algo = "ab_selfturn"
        

        # Initializes the board
        boardList = [0]*(self.pocketnum+1)*2
        for i in range(0,self.pocketnum):
            boardList[i] = self.ballnum
            boardList[i+self.pocketnum+1] = self.ballnum      
        self.board = boardList

     
    def display_board(self,board):
        
        # Displays the board
        print("AI:  \t {}   |   {} ".format(board[-1],  board[int(len(board)/2):-1][::-1] ) )
        print("Player:  \t {}   |   {} ".format(board[0:int(len(board)/2-1)], board[int(len(board)/2-1)]  ) )
        

    def scoop(self,board,pocket):
        
        # Takes balls from 'pocket'
        hand = board[pocket]
        board[pocket] = 0
        return hand,board

    def drop_balls(self,board,hand, next_pocket,player):
        
        # Sets the Kalaha that the current player should avoid
        if player:
            avoid = self.pocketnum*2+1   
        else:
            avoid = self.pocketnum
        
        # Drops balls into pockets (avoids dropping in opponents pocket)
        while hand > 0:
            if next_pocket != avoid: 
                board[next_pocket] += 1 
                hand -= 1   
                next_pocket = (next_pocket + 1) % len(board)                                  
            else:
                next_pocket = (next_pocket + 1) % len(board) # Go to next pocket - no drop of ball
                
            # Change in index in order for 'pocket_end' not to be 'out of bounds' wrt. the board
            pocket_end = next_pocket - 1
            if pocket_end == -1:
                pocket_end = len(board) - 1
            
        return pocket_end, hand, next_pocket, board
    
    
    def end_game(self,board):
        
        # If player 1 has all pockets emptied get player 2's balls    
        if all(e == 0 for e in board[0:self.pocketnum]):              
            board[self.pocketnum] = board[self.pocketnum] + sum(board[(self.pocketnum+1):(self.pocketnum*2+1)])
            board[(self.pocketnum+1):(self.pocketnum*2+1)] = [0]*self.pocketnum
               
        # If player 2 has all pockets emptied get player 1's balls
        elif all(e == 0 for e in board[(self.pocketnum+1):(self.pocketnum*2+1)]): 
            board[self.pocketnum*2+1] = board[self.pocketnum*2+1] + sum(board[0:self.pocketnum])
            board[0:self.pocketnum] = [0]*self.pocketnum

        total_balls = self.ballnum*self.pocketnum*2
        
        # If one player has more than half of the total balls, the respective player is the winner
        if board[self.pocketnum] > 0.5*total_balls: 
            return True, True, False, board
        elif board[self.pocketnum*2+1] > 0.5*total_balls:
            return True, False, False, board
        elif (board[self.pocketnum] == 0.5*total_balls) and (board[self.pocketnum*2+1] == 0.5*total_balls):
            return True, False, True, board
        else:
            return False, None, False, board
        

    def empty_pocket(self,board,pocket_end, player):
                                    
        # If anding in own empty pocket, then get ball from opposite pocket
        if player == True:
            if (pocket_end in list(range(0,self.pocketnum))) : 
                board[self.pocketnum] = board[self.pocketnum] + board[self.pocketnum*2-pocket_end] +  board[pocket_end]
                board[pocket_end] = 0
                board[self.pocketnum*2-pocket_end] = 0
                
            # Shift player turn
            player = False
            
        else:
            if (pocket_end in list(range(self.pocketnum+1,self.pocketnum*2+1))): # and (board.get_board()[12-index_end]>=1
                board[self.pocketnum*2+1] = board[self.pocketnum*2+1] + board[self.pocketnum*2-pocket_end] + board[pocket_end]
                board[pocket_end] = 0
                board[self.pocketnum*2-pocket_end] = 0   
            
            # Shift player turn
            player = True

        return player, board
    

    def make_move(self,board, field_choice,player):
        
        gameExit,winner = False,None
        
        hand,board = self.scoop(board,field_choice)  
        next_pocket = field_choice + 1
        
        while hand > 0:
        
            # Drop balls                   
            pocket_end, hand, next_pocket, board = self.drop_balls(board,hand, next_pocket,player) 
                
            # Set Kalaha for the current player
            if player:
                home = self.pocketnum
            else:
                home = self.pocketnum*2+1
        
            if pocket_end != home:
                # Last ball dropped in non-empty pocket
                if board[pocket_end] > 1: 
                    hand, board = self.scoop(board,pocket_end) 
           
                # Last ball dropped in empty pocket
                elif board[pocket_end] == 1: 
                    player,board = self.empty_pocket(board,pocket_end, player) 
                    
        # Check if game is over
        gameExit, winner, tie,board = self.end_game(board) 
          
        return gameExit,winner,tie,player,board


    def AI(self,board,maxDepth, algo):

        if algo == "minimax": 
            bestVal, path = self.minimax(maxDepth, True, board, False)
        
        elif algo == "ab":
            alpha = -1000 
            beta = 1000
            bestVal, path = self.alpha_beta(maxDepth, True, board, False, alpha, beta)
        
        elif algo == "ab_selfturn":
            alpha = -1000 
            beta = 1000
            bestVal, path = self.alpha_beta_selfturn(maxDepth, True, board, False, alpha, beta)
            
        elif algo == "ab_sumpockets":
            alpha = -1000 
            beta = 1000
            bestVal, path = self.alpha_beta_sumpockets(maxDepth, True, board, False, alpha, beta)
        
        return path, bestVal
    
    
    def get_pockets(self,AI):
        
        # Return the possible pocket choices
        if AI == True: 
            return  list(range(self.pocketnum+1,self.pocketnum*2+1)) 
            
        else:
            return  list(range(0,self.pocketnum)) 
        
    
    def minimax(self,maxDepth, isMaximizingPlayer, board, gameExit): 
        
        possible_choices = self.get_pockets(isMaximizingPlayer)
    
        # Terminating condition - leaf node is reached
        if (maxDepth == 0 ) or (gameExit):  
            #Calculate evaluation function and return this value
            eval_func = board[self.pocketnum*2+1]-board[self.pocketnum]
            return eval_func,[]
                
        # If current move is maximizer, find the maximum attainable value    
        if (isMaximizingPlayer): 

            bestVal = -10000
            ix = 0
            return_path = []
            child_path = []
         
            
            for i in possible_choices:
                if board[i] != 0:
                    gameexit,varUnused, varUnused, turn, moved_board = self.make_move(board.copy(),i,False)  # true when minimizing
                    
                    value,path = self.minimax(maxDepth-1, not turn, moved_board, gameexit)
                    
                    if value > bestVal:
                        bestVal = value
                        ix = i
                        child_path = path
                        
                    if gameexit:
                        break
                
            return_path = return_path + child_path + [ix]
                    
            return bestVal, return_path 
            
        # If current move is minimizer, find the minimum attainable value     
        else: 
            
            bestVal = 10000
            ix = 0
            return_path = []
            child_path = []
            
            for i in possible_choices:
                if board[i] != 0:
                    gameexit,varUnused, varUnused, turn, moved_board = self.make_move(board.copy(),i,True)
                    value,path = self.minimax(maxDepth-1, not turn, moved_board,gameexit)
                    
                    if value < bestVal:
                        bestVal = value
                        ix = i
                        child_path = path
                        
                
                    if gameexit:
                        break
            
            return_path = return_path + child_path + [ix]
            
            return bestVal, return_path
            
            
        
    def alpha_beta(self,maxDepth, isMaximizingPlayer, board, gameExit, alpha,beta): 
        
        possible_choices = self.get_pockets(isMaximizingPlayer)

        # Terminating condition - leaf node is reached
        if (maxDepth == 0 ) or (gameExit):  
                
            #Calculate evaluation function and return this value
            eval_func = board[self.pocketnum*2+1]-board[self.pocketnum]
            
            return eval_func,[]
                
        # If current move is maximizer, find the maximum attainable value    
        if (isMaximizingPlayer): 
            
            bestVal = -10000
            ix = 0
            return_path = []
            child_path = []

            for i in possible_choices:
                if board[i] != 0:
                    
                    gameexit,varUnused, varUnused,turn, moved_board = self.make_move(board.copy(),i,False)  # true when minimizing
                    value,path = self.alpha_beta(maxDepth-1, not turn, moved_board, gameexit, alpha,beta)
                    
                    if value > bestVal:
                        bestVal = value
                        ix = i
                        child_path = path
                        
                    if alpha  < bestVal:
                        alpha = bestVal
                        
                    if beta <= alpha:
                        break
  
                    if gameexit:
                        break

            return_path = return_path + child_path + [ix]
                    
            return bestVal, return_path 
            
        # If current move is minimizer, find the minimum attainable value     
        else: 

            bestVal = 10000
            ix = 0
            return_path = []
            child_path = []

            for i in possible_choices:
                if board[i] != 0:
                    
                    gameexit,varUnused,varUnused, turn, moved_board = self.make_move(board.copy(),i,True)
                    value,path = self.alpha_beta(maxDepth-1, not turn, moved_board,gameexit,alpha,beta)
                    
                    if value < bestVal:
                        bestVal = value
                        ix = i
                        child_path = path
                        
                    if beta  > bestVal:
                        beta = bestVal
                    
                    if beta <= alpha:
                        break
                
                    if gameexit:
                        break
            
            return_path = return_path + child_path + [ix]
           
           
            return bestVal, return_path
        
    
    def alpha_beta_selfturn(self,maxDepth, isMaximizingPlayer, board, gameExit, alpha,beta): 
        
        possible_choices = self.get_pockets(isMaximizingPlayer)

        # Terminating condition - leaf node is reached
        if (maxDepth == 0 ) or (gameExit):  
                
            #Calculate evaluation function and return this value
            eval_func = board[self.pocketnum*2+1]-board[self.pocketnum]
            
            if isMaximizingPlayer or gameExit:
                eval_func = eval_func + 100
            
            return eval_func,[]
                
        # If current move is maximizer, find the maximum attainable value    
        if (isMaximizingPlayer): 
            
            bestVal = -10000
            ix = 0
            return_path = []
            child_path = []

            for i in possible_choices:
                if board[i] != 0:
                    
                    gameexit,varUnused,varUnused, turn, moved_board = self.make_move(board.copy(),i,False)  # true when minimizing
                    value,path = self.alpha_beta_selfturn(maxDepth-1, not turn, moved_board, gameexit, alpha,beta)
                    
                    
                    if value > bestVal:
                        bestVal = value
                        ix = i
                        child_path = path
                        
                    if alpha  < bestVal:
                        alpha = bestVal
                        
                    if beta <= alpha:
                        break
  
                    if gameexit:
                        break

            return_path = return_path + child_path + [ix]
                    
            return bestVal, return_path 
            
        # If current move is minimizer, find the minimum attainable value     
        else: 

            bestVal = 10000
            ix = 0
            return_path = []
            child_path = []

            for i in possible_choices:
                if board[i] != 0:
                    
                    gameexit,varUnused,varUnused, turn, moved_board = self.make_move(board.copy(),i,True)
                    value,path = self.alpha_beta_selfturn(maxDepth-1, not turn, moved_board,gameexit,alpha,beta)
                    
                    if value < bestVal:
                        bestVal = value
                        ix = i
                        child_path = path
                        
                    
                    if beta  > bestVal:
                        beta = bestVal
                        
                        
                    if beta <= alpha:
                        break
                
                    if gameexit:
                        break
            
            return_path = return_path + child_path + [ix]
           
           
            return bestVal, return_path
    
    def alpha_beta_sumpockets(self,maxDepth, isMaximizingPlayer, board, gameExit, alpha,beta): 
        
        possible_choices = self.get_pockets(isMaximizingPlayer)

        # Terminating condition - leaf node is reached
        if (maxDepth == 0 ) or (gameExit):  
                
            #Calculate evaluation function and return this value
            eval_func = sum(board[0:self.pocketnum])-sum(board[(self.pocketnum+1):(self.pocketnum*2+1)])
            
            return eval_func,[]
                
        # If current move is maximizer, find the maximum attainable value    
        if (isMaximizingPlayer): 
            
            bestVal = -10000
            ix = 0
            return_path = []
            child_path = []

            for i in possible_choices:
                if board[i] != 0:
                    
                    gameexit,varUnused,varUnused, turn, moved_board = self.make_move(board.copy(),i,False)  # true when minimizing
                    value,path = self.alpha_beta_sumpockets(maxDepth-1, not turn, moved_board, gameexit, alpha,beta)
                    
                    
                    if value > bestVal:
                        bestVal = value
                        ix = i
                        child_path = path
                        
                    if alpha  < bestVal:
                        alpha = bestVal
                        
                    if beta <= alpha:
                        break
  
                    if gameexit:
                        break

            return_path = return_path + child_path + [ix]
                    
            return bestVal, return_path 
            
        # If current move is minimizer, find the minimum attainable value     
        else: 

            bestVal = 10000
            ix = 0
            return_path = []
            child_path = []

            for i in possible_choices:
                if board[i] != 0:
                    
                    gameexit,varUnused,varUnused, turn, moved_board = self.make_move(board.copy(),i,True)
                    value,path = self.alpha_beta_sumpockets(maxDepth-1, not turn, moved_board,gameexit,alpha,beta)
                    
                    if value < bestVal:
                        bestVal = value
                        ix = i
                        child_path = path
                        
                    
                    if beta  > bestVal:
                        beta = bestVal
                        
                        
                    if beta <= alpha:
                        break
                
                    if gameexit:
                        break
                    
            
            return_path = return_path + child_path + [ix]
           
           
            return bestVal, return_path
        
    
    
    def play(self):
        
        
        gameExit = False
    
        # initialize players
        print()
        player_choice = self.displayMenu(['Player', 'AI'],"Choose which player to start: ")        
        
        if player_choice == 1:
            player = True
        else:
            player = False
        
       
        # Game loop
        while not gameExit:
            
            print("================BOARD================")
             
            self.display_board(self.board)
            print("=====================================")
                
            if player:
                
                print("PLAYER'S TURN")
                
                while True:
                    field_choice = input("Choose a pocket (to exit game type 'x'): ")
                    if field_choice == 'x':
                        print("-----------------------------------")
                        print("Goodbye - hope to see you soon!")
                        print("-----------------------------------")
                        gameExit = True
                        break
                        
                    try:
                        field_choice = int(field_choice)
                        if field_choice in list(range(0,self.pocketnum)):
                            if self.board[field_choice] == 0:
                                print("The pocket is empty, pick another one")
                            else:
                                print("Field {} was chosen".format(field_choice))
                                break
                            
                        
                        else:
                            print("Not a valid pocket choice")
                    except:
                        print('Please enter a number')
                
                if gameExit:
                    break
                
                gameExit, winner, tie, player, self.board = self.make_move(self.board,field_choice,player)
                
            else: 
                
                print("AI'S TURN")
                
                time.sleep(2) # Suspends execution in order for player to grasp AI's choice 
 
                # Timing of the AI
                t0 = time.time()
                path, eval_func = self.AI(self.board,self.depth, self.algo)
                t1 = time.time()
                path = path[::-1]
                total = t1-t0
                
                print("AI execution time = {:.6f} seconds".format(total))
                
                # Getting sequence of AI's pocket choices
                ai_feas = list(range(self.pocketnum+1,self.pocketnum*2+1))
                
                # Executing AI's pocket choices by iterating through sequence of AI's pocket choices
                for field_choice in path:
                    
                    if field_choice in ai_feas: 
                       gameExit, winner, tie, player, self.board = self.make_move(self.board,field_choice,player)
                    
                    else:
                        player = True
                        break
                    
            # Printing result if game is over      
            if gameExit:        
                if tie == True:
                    print("**** GAME OVER - IT IS A TIE ****")
                    self.display_board(self.board)
                elif winner == True:
                    print("**** GAME OVER - PLAYER IS THE WINNER ****")
                    self.display_board(self.board)
                elif winner == False:
                    print("**** GAME OVER - AI IS THE WINNER ****")
                    self.display_board(self.board)
                           

def main():        
    g = Game()
    g.play()

if __name__ == "__main__":
    main()