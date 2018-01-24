from euchreGameMaster import SUITS
from euchreGameMaster import POSITIONS
from euchreGameMaster import RANK
from euchreGameMaster import BIDS
from euchreGameMaster import Call

class Player(object) :
    def isValidPlay(self,card,suitLed) :
        if suitLed is None :
            return card in self.hand
 
        cardsInSuit = [c for c in self.hand if c.suit == suitLed];
        if len(cardsInSuit) == 0 :
            return card in self.hand
         
        return card in cardsInSuit
 
    def isValidBid(self,bid,upcard,auctionRound) :
        if auctionRound == 0 and not bid.suit == Call(BIDS.passbid).getSuit() and not bid.suit == upcard.suit :
            return False
        if auctionRound == 1 and bid.suit == upcard.suit :
            return False
        if auctionRound == 1 and self.dealer == self.position and bid.suit == Call(BIDS.passbid).getSuit():
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
        return Call(BIDS.passbid)
 
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

        for i in xrange(len(self.hand)):
            for j in xrange(i+1, len(self.hand)):
                if self.hand[j].scoreForBiddingRoundOne(suit) > self.hand[i].scoreForBiddingRoundOne(suit):
                    self.hand[i], self.hand[j] = self.hand[j], self.hand[i]
                    
                    

    def sortForBiddingRoundTwo(self, suit):

        for i in xrange(len(self.hand)):
            for j in xrange(i+1, len(self.hand)):
                if self.hand[j].scoreForBiddingRoundTwo(suit) > self.hand[i].scoreForBiddingRoundTwo(suit):
                    self.hand[i], self.hand[j] = self.hand[j], self.hand[i]
                    
        

    def sortForPlay(self, suit):

        for i in xrange(len(self.hand)):
            for j in xrange(i+1, len(self.hand)):
                if self.hand[j].scoreForPlay(suit) > self.hand[i].scoreForPlay(suit):
                    self.hand[i], self.hand[j] = self.hand[j], self.hand[i]
                    



