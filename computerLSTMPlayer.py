import random
import numpy as np
import torch
import torch.nn as nn
from torch.optim import Adam
from euchreGameMaster import SUITS
from euchreGameMaster import RANKS
from euchreGameMaster import EuchreCard as Card
from euchreGameMaster import BIDS
from player import Player

# Define some game-related constants
cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]
all_actions = [('deal',dealer,upcard) for dealer in range(4) for upcard in cards]
all_actions.extend(('bid',player,bid) for player in range(4) for bid in BIDS)
all_actions.extend(('play',player,card) for player in range(4) for card in cards)
all_actions.extend(('play',player,None) for player in range(4))
all_actions.extend(('score',value) for value in [1,2,4,-1,-2,-4])
all_actions.extend(('hand',card) for card in cards)

numPlayers = 4
handSize = 5

# Define some learning-related constants
batchSize = 50

# Class to handle construction and training of the neural net
class LMAgent(nn.Module):
	def __init__(self, action_embedding_size,hidden_size,memory_max_size):
		super(LMAgent,self).__init__()
		self.embedding = nn.Embedding(len(all_actions),action_embedding_size)
		self.lstm = nn.LSTM(input_size=action_embedding_size, hidden_size=hidden_size)
		self.h0 = nn.parameter.Parameter(torch.zeros((1,1,hidden_size)))
		self.c0 = nn.parameter.Parameter(torch.zeros((1,1,hidden_size)))
		self.output = nn.Linear(hidden_size, len(all_actions))
		self.memory = [None] * memory_max_size
		self.optimizer = Adam(self.parameters())

	def remember(self, game_transcript):
		idx = random.randrange(len(self.memory))
		self.memory[idx] = torch.tensor(game_transcript)

	def runout(self, prefix, max_steps):
		inp = torch.unsqueeze(torch.tensor(prefix),1)
		hn = self.h0
		cn = self.c0
		for _ in range(max_steps-len(prefix)):
			out, (hn,cn) = self.lstm(self.embedding(inp),(hn,cn))
			next_action = torch.argmax(self.output(out[-1,0,:]))
			if all_actions[next_action][0] == 'score':
				return all_actions[next_action][1]
			inp = next_action.reshape((1,1))
		return 0

	def act(self, current_history, valid_actions):
		with torch.no_grad():
			# 29 is the maximum number of actions that will happen in a game
			return max(valid_actions, key=lambda x:self.runout(current_history+[all_actions.index(x)], 29))

	def train(self):
		loss_fcn = nn.CrossEntropyLoss()
		total_loss = torch.zeros((1))
		for transcript in self.memory:
			if transcript is not None:
				embeddings = torch.unsqueeze(self.embedding(transcript),1)
				self.predictions = self.output(self.lstm(embeddings,(self.h0,self.c0))[0])
				total_loss += loss_fcn(self.predictions[5:-1,0,:],transcript[6:]) # The first 5 are just the deal
		self.optimizer.zero_grad()
		total_loss.backward()
		self.optimizer.step()

	def save(self, name):
		torch.save({'model_state_dict':self.state_dict(),'memory':self.memory},name)

	def load(self, name):
		checkpoint = torch.load(name)
		if 'model_state_dict' in checkpoint and 'memory' in checkpoint:
			self.load_state_dict(checkpoint['model_state_dict'])
			self.memory = checkpoint['memory'] + []*(memory_max_size-len(checkpoint['memory']))
		else:
			self.load_state_dict(checkpoint)

# The actual computer player class.  
class ComputerPlayer(Player) :
	def __init__(self, brain=None, update_frequency=1000) :
		super(ComputerPlayer, self).__init__()
		if brain is None :
			self.brain = LMAgent(64,1024,10000)
		else :
			self.brain = brain
		self.update_frequency = update_frequency
		self.hands_played = 0

	def makeBid(self,currentRound,upCard,dealer) :
		if currentRound == 0:
			valid_bids = [bid for bid in BIDS if bid.getSuit() == upCard.suit]
		else:
			valid_bids = [bid for bid in BIDS if bid.getSuit() != upCard.suit]
		return self.brain.act(self.transcript, [('bid',0,bid) for bid in valid_bids])[2]

	def playCard(self, suitLed, trick=None) :
		if suitLed and any(card.suit == suitLed for card in self.hand):
			valid_plays = [('play',0,card) for card in self.hand if card.suit == suitLed]
		else:
			valid_plays = [('play',0,card) for card in self.hand if card]
		
		play = self.brain.act(self.transcript, valid_plays)[2]
		self.hand.remove(play)
		return play

	def swapUpCard(self, upcard) :
		self.hand.append(upcard)
		self.sortForPlay(upcard.suit)
		self.hand = self.hand[1:]

	def announceGameStart(self,hand,upcard,dealer,position) :
		super(ComputerPlayer,self).announceGameStart(hand,upcard,dealer,position)
		self.transcript = list(all_actions.index(('hand',card)) for card in hand)+[all_actions.index(('deal',self.positionToIndex(dealer),upcard))]
			
	def announceBidMade(self, bid, player) :
		if bid.getSuit() is not BIDS.passbid:
			self.announceTrumpSuit(bid.getSuit())
		self.transcript.append(all_actions.index(('bid',self.positionToIndex(player),bid)))

	def announceCardPlayed(self,card, player) :
		self.transcript.append(all_actions.index(('play',self.positionToIndex(player),card)))

	def announceGameEnd(self, score) :
		self.transcript.append(all_actions.index(('score',score)))
		self.brain.remember(self.transcript)
		self.hands_played += 1
		if self.hands_played % self.update_frequency == 0:
			self.brain.train()

	def save(self, name):
		self.brain.save(name)

	def load(self, name):
		self.brain.load(name)



