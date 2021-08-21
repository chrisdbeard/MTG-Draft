# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 11:05:07 2021

@author: Chris
"""
from enum import Enum
import random
import os
import pathlib

#TODO account for rarity in card list


class Rarity(Enum):
    UNDEFINED = 0
    LAND = 1
    COMMON = 2
    UNCOMMON = 3
    RARE = 4
    MYTHIC = 5
    
    
class CardType(Enum):
    UNDEFINED = 0
    LAND = 1
    CREATURE = 2
    INSTANT = 3
    SORCERY = 4
    ARTIFACT = 5
    TRIBAL = 6
    PLANESWALKER = 7
 
    
class Deck:
     
     
     def __init__(self):
         self.cards = []
         
         
     def add_card(self, card_to_add):
         # no cards in list yet.
         if len(self.cards) == 0:
             self.cards.append([card_to_add, 1])
         #there are cards in the deck already, check for duplicates.
         else:
             found_duplicate = False
             for i,(existing_card, qty) in enumerate(self.cards):
                 # the card exist in the deck already, increment the qty
                 if card_to_add.name == existing_card.name:
                     self.cards[i] = [existing_card, qty + 1] 
                     found_duplicate = True
                     break
             # the card is new to the deck
             if not found_duplicate:
                 self.cards.append([card_to_add, 1])
             
    
class Pack:
    num_cards = 15
    
    
    def __init__(self, list_of_cards):
        self.cards = list_of_cards
    
    
    def __str__(self):
        output_string = ""
        for i, card in enumerate(self.cards):
            output_string += f"{i}: {card.name}\n"
        return output_string
        
       
    def remove_card_by_name(self, card_name):
        for card in self.cards:
            if card.name == card_name:
                self.cards.remove(card)
                break
    
       
class Card:


    def __init__(self, name, rarity, cmc, card_type):
        self.name = name
        self.rarity = rarity
        self.cmc = cmc
        self.card_type = card_type
        
        

class CardSet:
    
    
    def __init__(self, passed_file_path):
        self.file_path = passed_file_path
        self.cards = self.read_file()
        self.num_cards_in_set = len(self.cards)
        
    
    def read_file(self,):
        with open(self.file_path, 'r') as fh:
            lines = fh.readlines()
            # drop first row. it's not a card.
            lines = lines[1:]
            # remove the first 2 chars from each card.
            # it describes how many versions there are
            # and we dont need that information.
            idx = 0
            for line in lines:
                lines[idx] = line[2:]
                idx += 1
            list_of_cards = []
            for card_name in lines:
                card = Card(card_name, Rarity.UNDEFINED, None, CardType.UNDEFINED)
                list_of_cards.append(card)
            return list_of_cards
       
    
    def get_pack(self,):
        list_of_cards = []
        for i in range(Pack.num_cards):
            random_idx = random.randint(0, self.num_cards_in_set - 1)
            random_card = self.cards[random_idx]
            list_of_cards.append(random_card)
        pack = Pack(list_of_cards)
        return pack


class MTGDraft:
    num_seats = 8
    num_packs_per_player = 3
    
    
    def __init__(self, card_set_file_path):
        self.card_set = CardSet(card_set_file_path)
        self.players = []
        self.packs = []
        
        
    def start_game(self):
        self.add_user_as_player()
        self.make_bots()
        self.seat_players()
        self.get_packs_for_draft()
        for i in range(self.num_packs_per_player):
            self.distribute_packs()
            for j in range(Pack.num_cards):
                self.select_cards()
                self.pass_packs()
        self.write_decks_to_files()
        breakpoint
        
           
    def make_bots(self):
        # assume always only one human player
        num_bots = self.num_seats - 1
        for i in range(num_bots):
            bot_name = f"Bot_{i + 1}"
            bot = Player(bot_name, False)
            self.players.append(bot)
            
            
    def add_user_as_player(self):
        name = input("Enter your name: ")
        self.players.append(Player(name, True))
        

    def seat_players(self):
        # shuffle the list of players
        random.shuffle(self.players)
        # use their new indexes in self.player to set their seat numbers
        for i, player in enumerate(self.players):
            player.seat_num = i
    
    
    def get_packs_for_draft(self):
        num_packs = self.num_seats * self.num_packs_per_player
        for i in range(num_packs):
            pack = self.card_set.get_pack()
            self.packs.append(pack)
            
            
    def distribute_packs(self):
        for player in self.players:
            pack = self.packs.pop(0)
            player.current_pack = pack
            
    
    def select_cards(self):
        for player in self.players:
            player.select_card()
            
            
    def pass_packs(self):
        packs = []
        # gather the packs from all players.
        for player in self.players:
            packs.append(player.current_pack)
            player.current_pack = None
        # rotate the list of packs.
        packs = packs[1:] + packs[:1]
        # reissue the packs.
        for player in self.players:
            player.current_pack = packs.pop(0)
            
    
    def write_decks_to_files(self):
        cwd = pathlib.Path(os.getcwd())
        saved_decks_folder = cwd / "Saved Decks"
        saved_decks_folder.mkdir(parents = True, exist_ok = True)
        for player in self.players:
            full_file_path = saved_decks_folder / player.name
            with open(full_file_path.with_suffix(".dec"), "w") as fh:
                for card, qty in player.deck.cards:
                    fh.write(f"{qty} {card.name}")
    
    
class Player:
    
    
    def __init__(self, name, human):
        self.name = name
        self.human = human
        self.deck = Deck()
        self.packs_in_queue = []
        self.current_pack = None
        self.seat_num = None
        

    def select_card(self):
        # let the human choose.
        if self.human:
            print("This is your current pack\n")
            print(self.current_pack)
            user_input = input("Choose a card by index number: ")
            if user_input.isnumeric():
                if int(user_input) < len(self.current_pack.cards):
                     selected_card = self.current_pack.cards.pop(int(user_input))
                     self.deck.add_card(selected_card)
                     return selected_card
                # user input out of range.
                else:
                    print("Index out of range")
                    selected_card = self.select_card()
                    if selected_card != None:
                        return selected_card
                    else:
                        return None
            # user input not numeric
            else:
                print("Invalid input")
                selected_card = self.select_card()
                if selected_card != None:
                        return selected_card
                else:
                    return None
        # if the player is a bot.
        else:
            random_idx = random.randint(0, len(self.current_pack.cards) - 1)
            selected_card = self.current_pack.cards.pop(random_idx)
            self.deck.add_card(selected_card)
            return selected_card


def main():
    # use file of set you wish to draft(.dec format)
    card_set_path = r"afr.dec"
    my_draft = MTGDraft(card_set_path)
    my_draft.start_game()
    

if __name__ == '__main__':
    main()