import random
import numpy as np
from euchreGameMaster import SUITS
from euchreGameMaster import POSITIONS
from euchreGameMaster import RANK
from euchreGameMaster import EuchreCard as Card
from euchreGameMaster import Call
from euchreGameMaster import BIDS
from euchreGameMaster import GameMaster 
from player import Player
from collections import deque
from keras.models import Model
from keras.layers import Dense, Input, Concatenate, Flatten
from keras.optimizers import Adam

# Define some game-related constants
cards = [Card(suit, rank) for suit in [SUITS.CLUB, SUITS.DIAMOND, SUITS.HEART, SUITS.SPADE, SUITS.TRUMP]
	 for rank in range(9,17)]
cardIndex = {}
for i in range(len(cards)) :
	cardIndex[cards[i]] = i
cardIndex[None] = None

bids = [Call([SUITS.CLUB, True]), Call([SUITS.CLUB, False]),
	Call([SUITS.DIAMOND, True]), Call([SUITS.DIAMOND, False]),
	Call([SUITS.HEART, True]), Call([SUITS.HEART, False]),
	Call([SUITS.SPADE, True]), Call([SUITS.SPADE, False]),
	Call([None,None])]
bidIndex = {}
for i in range(len(bids)) :
	bidIndex[bids[i]] = i

numPlayers = 4
handSize = 5

# Define some learning-related constants
batchSize = 50

# Class with some utility functions to parse the output of the neural net
class PlayRanking :
	def __init__(self,bidScores,cardScores,swapScores) :
		self.bidScores = bidScores
		self.cardScores = cardScores
		self.swapScores = swapScores
		
	def getBids(self) :
		return [b for _,b in sorted(zip(self.bidScores,range(len(bids))))]
	
	def getCards(self) :
		return [c for _,c in sorted(zip(self.cardScores,range(len(cards))))]

	def getSwaps(self) :
		return [c for _,c in sorted(zip(self.swapScores,range(len(cards))))]

# Class to handle construction and training of the neural net
# modified from https://github.com/keon/deep-q-learning
class DQNAgent:
	def __init__(self, action_size):
		self.action_size = action_size
		self.memory = deque(maxlen=2000)
		self.gamma = 0.95    # discount rate
		self.epsilon = 1.0  # exploration rate
		self.epsilon_min = 0.01
		self.epsilon_decay = 0.995
		self.learning_rate = 0.001
		self.model = self._build_model()

	def _build_model(self):
		# Neural Net for Deep-Q learning Model
		initialHand = Input(shape=(handSize,len(cards)),name='initialHand')
		actionCounter = Input(shape=(numPlayers-1,),name='actionCounter')
		upcard = Input(shape=(len(cards),),name='upcard')
		bidHistory = Input(shape=(numPlayers,len(bids),2*numPlayers),name='bidHistory')
		currentHand = Input(shape=(handSize,len(cards)),name='currentHand')
		playHistory = Input(shape=(handSize,numPlayers,len(cards)),name='playHistory')

		nextLayer = Concatenate()([Flatten()(initialHand),
					(actionCounter),
					(upcard),
					Flatten()(bidHistory),
					Flatten()(currentHand),
					Flatten()(playHistory)])

		nextLayer = Dense(200,activation='relu')(nextLayer)
		nextLayer = Dense(400,activation='relu')(nextLayer)
		nextLayer = Dense(50,activation='relu')(nextLayer)
		output = Dense(self.action_size,activation='linear')(nextLayer)

		model = Model(inputs = [initialHand,actionCounter,upcard,bidHistory,currentHand,playHistory],
			      outputs = output)
		model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))        
		
		return model

	def remember(self, state, action, reward, next_state, done):
		self.memory.append((state, action, reward, next_state, done))

	def act(self, state):
		if np.random.rand() <= self.epsilon :
			response = np.random.randn(self.action_size,)
		else :
			response = self.model.predict(state)
		return PlayRanking(response[:len(bids)],response[len(bids):len(bids)+len(cards)],
				   response[len(bids)+len(cards):])
        
	def replay(self, batch_size):
		minibatch = random.sample(self.memory, batch_size)
		for state, action, reward, next_state, done in minibatch:
			target = reward
			if not done:
				target = (reward + self.gamma *
					  np.amax(self.model.predict(next_state)[0]))
			target_f = self.model.predict(state)
			target_f[0][action] = target
			self.model.fit(state, target_f, epochs=1, verbose=0)
		if self.epsilon > self.epsilon_min:
			self.epsilon *= self.epsilon_decay

	def load(self, name):
		self.model.load_weights(name)

	def save(self, name):
		self.model.save_weights(name)

# The actual computer player class.  Internally, all bids and cards are actually stored as indices
# into the bid and card lists (defined at the top of the file)
class ComputerPlayer(Player) :
	def __init__(self, brain=None) :
		super(ComputerPlayer, self).__init__()
		self.currentBidRound = 0
		self.currentTrick = 0
		if brain is None :
			# The first group are bids, the next group is cards, the last group is cards to swap
			self.brain = DQNAgent(len(bids)+2*len(cards))
		else :
			self.brain = brain
		

	def doSomething(self) :
		if self.lastState is not None :
			self.brain.remember(self.lastState,self.lastAction,0,self.gameState,False)
		self.lastState = self.gameState
		return self.brain.act(self.gameState)

	def makeBid(self,currentRound,upCard,dealer) :
		rankings = self.doSomething()
		self.lastAction = [r for r in rankings.getBids() if 
				   self.isValidBid(bids[r],upCard,currentRound)][0]
		print bids[self.lastAction]
		return bids[self.lastAction]

	def playCard(self, suitLed, trick=None) :
		rankings = self.doSomething()
		self.lastAction = [r for r in rankings.getCards() if self.isValidPlay(cards[r], suitLed)][0]
		# Don't forget to remove the card from our hand
		self.gameState['currentHand'][:,self.lastAction] = 0
		self.hand.remove(cards[self.lastAction])
		return cards[self.lastAction]

	def swapUpCard(self) :
		rankings = self.doSomething()
		self.lastAction = [r for r in rankings.getSwaps() if cards[r] in self.hand][0]
		self.hand.remove(cards[self.lastAction])
		self.hand.append(self.upcard)
		# Now we have to resort the hand again since it has changed.
		self.announceTrumpSuit(self.upcard.suit)
		
	def announceGameStart(self,hand,upcard,dealer,position) :
		super(ComputerPlayer,self).announceGameStart(hand,upcard,dealer,position)
		self.position = position
		self.hand = hand
		self.upcard = upcard
		self.dealer = dealer

		self.gameState = {}
		self.gameState['initialHand'] = np.zeros((handSize,len(cards)))
		# Sort initial hand and fill in the initialHand matrix
		self.gameState['actionCounter'] = np.zeros((numPlayers-1,), dtype=np.int)
		self.gameState['upcard'] = np.zeros((len(cards),))
		self.gameState['upcard'][cardIndex[upcard]] = 1
		self.gameState['bidHistory'] = np.zeros((numPlayers,len(bids),2*numPlayers))
		self.gameState['currentHand'] = np.zeros((handSize,len(cards)))
		self.gameState['playHistory'] = np.zeros((handSize,numPlayers,len(cards)))
		self.lastState = None
		self.lastAction = None
		

	def incrementActionCounter(self) :
		if sum(self.gameState['actionCounter']) == 3 :
			self.gameState['actionCounter'] = np.zeros((numPlayers-1,), dtype=np.int)
		else :
			self.gameState['actionCounter'][sum(self.gameState['actionCounter'])] = 1

	def announceBidMade(self,bid, player) :
		self.gameState['bidHistory'][self.positionToIndex(player),bidIndex[bid],self.currentBidRound] = 1
		self.incrementActionCounter()
		self.currentBidRound += 1

	def announceCardPlayed(self,card, player) :
		self.gameState['playHistory'][self.currentTrick/4,self.positionToIndex(player),cardIndex[card]] = 1
		self.incrementActionCounter()
		self.currentTrick += 1

	def announceGameEnd(self,score) :
		if self.lastState is not None:
			self.brain.remember(self.lastState,self.lastAction,score,self.gameState,True)
		if len(self.brain.memory) > batchSize :
			self.brain.replay(batchSize)

	def announceTrumpSuit(self,suit) :
		super(ComputerPlayer,self).announceTrumpSuit(suit)
		# Resort hand by new trump values and fill in the currentHand matrix (don't assume that it's already 0's)
		self.trump = suit


	def save(self, name):
		self.brain.save(name)

	def load(self, name):
		self.brain.load(name)



