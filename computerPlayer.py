import random
import numpy as np
from euchreGameMaster import SUITS
from euchreGameMaster import POSITIONS
from euchreGameMaster import RANKS
from euchreGameMaster import EuchreCard as Card
from euchreGameMaster import BIDS
from euchreGameMaster import GameMaster 
from player import Player
from collections import deque
from keras.models import Model
from keras.layers import Dense, Input, Concatenate, Flatten
from keras.optimizers import Adam

# Define some game-related constants
cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]
cardIndex = {}
for i in range(len(cards)) :
	cardIndex[cards[i]] = i
cardIndex[None] = None

bidIndex = dict((x,i) for i,x in enumerate(BIDS))
bids = [b for b in BIDS]

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
		return [b for _,b in sorted(zip(self.bidScores,range(len(BIDS))))]
	
	def getCards(self) :
		return [c for _,c in sorted(zip(self.cardScores,range(len(cards))))]

	def getSwaps(self) :
		return [c for _,c in sorted(zip(self.swapScores,range(len(cards))))]

# Class to handle construction and training of the neural net
# modified from https://github.com/keon/deep-q-learning
class DQNAgent:
	def __init__(self, action_size,epsilon=1.0,epsilon_min=0.01,epsilon_decay=0.995):
		self.action_size = action_size
		self.memory = deque(maxlen=2000)
		self.gamma = 0.95    # discount rate
		self.epsilon = epsilon  # exploration rate
		self.epsilon_min = epsilon_min
		self.epsilon_decay = epsilon_decay
		self.learning_rate = 0.001
		self.model = self._build_model()

	def _build_model(self):
		# Neural Net for Deep-Q learning Model
		initialHand = Input(shape=(handSize,len(cards)),name='initialHand')
		actionCounter = Input(shape=(numPlayers-1,),name='actionCounter')
		upcard = Input(shape=(len(cards),),name='upcard')
		bidHistory = Input(shape=(numPlayers,len(BIDS),2*numPlayers),name='bidHistory')
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
			response = self.model.predict(state)[0]
		if len(response) < len(BIDS) :
			print (len(response))
		return PlayRanking(response[:len(BIDS)],response[len(BIDS):len(BIDS)+len(cards)],
				   response[len(BIDS)+len(cards):])
        
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
			self.brain = DQNAgent(len(BIDS)+2*len(cards))
		else :
			self.brain = brain
		
	def doSomething(self) :
		if self.lastState is not None :
			self.brain.remember(self.lastState,self.lastAction,0,self.gameState,False)
		self.lastState = self.gameState
		return self.brain.act(self.gameState)

	def makeBid(self,currentRound,upCard,dealer) :
		rankings = self.doSomething()
		if currentRound > 0:
			self.sortForBiddingRoundTwo(self.upcard.getSuit())
			self.setHandState('currentHand')
		self.lastAction = [r for r in rankings.getBids() if 
				   self.isValidBid(bids[r],upCard,currentRound)][0]
		return bids[self.lastAction]

	def playCard(self, suitLed, trick=None) :
		rankings = self.doSomething()
		choice = [r for r in rankings.getCards() if self.isValidPlay(cards[r], suitLed)]
		if len(choice) < 1 :
			print len(rankings.getCards())
			print rankings.cardScores
			print [str(c) for c in self.hand]
			print suitLed
		self.lastAction = choice[0]
		# Don't forget to remove the card from our hand
		self.gameState['currentHand'][0,:,self.lastAction] = 0
		self.hand.remove(cards[self.lastAction])
		
		return cards[self.lastAction]

	def swapUpCard(self) :
		rankings = self.doSomething()
		self.hand.append(self.upcard)
		self.sortForPlay(self.trump)
		self.lastAction = [r for r in rankings.getSwaps() if cards[r] in self.hand][0]
		self.hand.remove(cards[self.lastAction])
		#self.sortForPlay(self.trump)
		# Now we have to reload the self.gamestate the hand again since it has changed.
		self.resetCurrentHand()
		self.announceTrumpSuit(self.upcard.suit)


	def resetCurrentHand(self):
		self.gameState['currentHand'] = np.zeros((1,handSize,len(cards)))
		for i in xrange(len(self.hand)):
			self.gameState['currentHand'][0,i,cardIndex[self.hand[i]]] = 1


	def announceGameStart(self,hand,upcard,dealer,position) :
		super(ComputerPlayer,self).announceGameStart(hand,upcard,dealer,position)
		self.position = position
		self.hand = hand
		self.upcard = upcard
		self.dealer = dealer
		self.currentTrick = 0
		self.currentBidRound = 0

		self.gameState = {}
		self.sortForBiddingRoundOne(self.upcard.getSuit())
		self.setHandState('initialHand')
		self.gameState['actionCounter'] = np.zeros((1,numPlayers-1,), dtype=np.int)
		self.gameState['upcard'] = np.zeros((1,len(cards)))
		self.gameState['upcard'][0,cardIndex[upcard]] = 1
		self.gameState['bidHistory'] = np.zeros((1,numPlayers,len(BIDS),2*numPlayers))
		self.gameState['currentHand'] = np.zeros((1,handSize,len(cards)))
		self.gameState['playHistory'] = np.zeros((1,handSize,numPlayers,len(cards)))
		self.lastState = None
		self.lastAction = None
		self.gameState['currentHand'] = self.gameState['initialHand']


	def incrementActionCounter(self) :
		if sum(sum(self.gameState['actionCounter'])) == 3 :
			self.gameState['actionCounter'] = np.zeros((1,numPlayers-1), dtype=np.int)
		else :
			self.gameState['actionCounter'][sum(self.gameState['actionCounter'])] = 1

	def setHandState(self,field) :
		self.gameState[field] = np.zeros((1,handSize,len(cards)))
		for i in xrange(len(self.hand)):
			self.gameState[field][0,i,cardIndex[self.hand[i]]] = 1
			

	def announceBidMade(self,bid, player) :
		if bid.getSuit() is not BIDS.passbid:
			self.announceTrumpSuit(bid.getSuit())
			self.sortForPlay(bid.getSuit())
			self.setHandState('currentHand')
		self.gameState['bidHistory'][0,self.positionToIndex(player),bidIndex[bid],self.currentBidRound] = 1
		self.incrementActionCounter()
		self.currentBidRound += 1

	def announceCardPlayed(self,card, player) :
		self.gameState['playHistory'][0,self.currentTrick/4,
					      self.positionToIndex(player),cardIndex[card]] = 1
		self.incrementActionCounter()
		self.currentTrick += 1

	def announceGameEnd(self,score) :
		if self.lastState is not None:
			self.brain.remember(self.lastState,self.lastAction,score,self.gameState,True)
		if len(self.brain.memory) > batchSize :
			self.brain.replay(batchSize)

	def announceTrumpSuit(self,suit) :
		for card in self.hand:
			card.declareTrump(suit)
		self.trump = suit

	def save(self, name):
		self.brain.save(name)

	def load(self, name):
		self.brain.load(name)



