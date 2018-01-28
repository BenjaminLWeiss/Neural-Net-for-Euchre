from euchreGameMaster import SUITS
from euchreGameMaster import POSITIONS
from euchreGameMaster import RANKS
from euchreGameMaster import BIDS

class Player(object) :
    def isValidPlay(self,card,suitLed) :
        if suitLed is None :
            return card in self.hand
 
        cardsInSuit = [c for c in self.hand if c.suit == suitLed];
        if len(cardsInSuit) == 0 :
            return card in self.hand
         
        return card in cardsInSuit
 
    def isValidBid(self,bid,upcard,auctionRound) :
        if auctionRound == 0 and bid.getSuit() is not None and not bid.getSuit() == upcard.suit :
            return False
        if auctionRound == 1 and bid.getSuit() == upcard.suit :
            return False
        if auctionRound == 1 and self.dealer == self.position and bid.getSuit() is None:
            return False

        return True

    def positionToIndex(self,position) :
        return (position-self.position) % 4
 
    def announceGameStart(self, hand, upcard, dealer, position) :
        self.hand = hand
        self.dealer = dealer
        self.position = position
        self.upcard = upcard
         
    def announceTrumpSuit(self, suit) :
        for card in self.hand :
            card.declareTrump(suit)
 
    #Subclasses can override these to actually do something intelligent
    def makeBid(self, auctionRound, upcard, dealer) :
        return BIDS.passbid
 
    def playCard(self, suitLed, trick=None) :
        validCards = [c for c in self.hand if self.isValidPlay(c,suitLed)]
        cardToPlay = validCards[0]
        self.hand.remove(cardToPlay)
        return cardToPlay
 
    def announceBidMade(self, bid, player) :
        pass
 
    def announceCardPlayed(self, card, player) :
        pass
 
    def announceGameEnd(self,score) :
        pass
 
    def swapUpCard(self):
        pass

    def sortForBiddingRoundOne(self, suit):
		def score(card):
		    score = card.getRank().value
		    if card.getSuit() == suit:
		        if score == 11: score += 5
		        score += 20
		    if score == 11:
		        if suit == SUITS.spades and card.getSuit() == SUITS.clubs:
		            score += 24
		        elif suit == SUITS.hearts and card.getSuit() == SUITS.diamonds:
		            score += 24
		        elif suit == SUITS.diamonds and card.getSuit() == SUITS.hearts:
		            score += 24
		        elif suit == SUITS.clubs and card.getSuit() == SUITS.spades:
		            score += 24

		    return score

		self.hand = sorted(self.hand,key=score)                   

    def sortForBiddingRoundTwo(self, suit):
		def score(card):
		    score = card.getRank().value
		    if card.getSuit() == suit:
		        score -= 10
		    if score == 11:
		        score += 15
		    return score

		self.hand = sorted(self.hand,key=score)
        

    def sortForPlay(self, suit):
		def score(card):
		    score = card.getRank().value
		    if card.getSuit() == SUITS.trump:
		        score += 10
		    
		    if card.getSuit() == SUITS.spades and suit == SUITS.clubs:
		        score -= 2
		    elif card.getSuit() == SUITS.hearts and suit == SUITS.diamonds:
		        score -= 2
		    elif card.getSuit() == SUITS.diamonds and suit == SUITS.hearts:
		        score -= 2
		    elif card.getSuit() == SUITS.clubs and suit == SUITS.spades:
		        score -= 2

		    return score

		self.hand = sorted(self.hand,key=score)

