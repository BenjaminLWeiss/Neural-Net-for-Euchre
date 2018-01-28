#from __future__ import print_function
import curses
from euchreGameMaster import SUITS
from euchreGameMaster import POSITIONS
from euchreGameMaster import EuchreCard
from euchreGameMaster import BIDS
from euchreGameMaster import GameMaster 
from player import Player
from pick import Picker

#def go_back(picker):
#    return (None, -1)
cardinalDirections = {}
cardinalDirections[0] = 'West'
cardinalDirections[1] = 'North'
cardinalDirections[2] = 'East'
cardinalDirections[3] = 'South'

class HumanPlayer(Player):

    def __init__(self):
        super(HumanPlayer, self).__init__()
        self.playToTrick = 0

    def makeBid(self, auctionRound, upcard, dealer_position):
        
        raw_input("Press Enter to continue...")
#        self.informUpCard(auctionRound)
        if auctionRound == 0:
            self.sortForBiddingRoundOne(self.upcard.getSuit())
            title = 'The upcard is %s. \n Your hand is %s. \n Would you like to Bid, or Pass?' % (self.upcard,
                                                                                                  self.convertHandToText())
        else:
            self.sortForBiddingRoundTwo(self.upcard.getSuit())
            title = 'The upcard was %s. \n Your hand is %s. \n Would you like to Bid, or Pass?' % (self.upcard,
                                                                                                   self.convertHandToText())
        options = ['Bid', 'Pass']
        
        picker = Picker(options, title)
        #picker.register_custom_handler(curses.KEY_LEFT, go_back)
        option, index = picker.start()
        
        if option == 'Bid':
            trialBid = self.selectTrump()
            if self.isValidBid(trialBid,self.upcard, auctionRound):
                return trialBid
            else:
                print 'That is not a legal choice. The only bid you may make is the suit of the up card.'
                return self.makeBid(auctionRound, upcard, dealer_position)
            
        elif option == 'Pass':
            if self.isValidBid(BIDS.passbid, self.upcard, auctionRound):
                return BIDS.passbid
            else:
				print self.upcard, auctionRound
                print "You may not passout the hand"
                return self.makeBid(auctionRound, upcard, dealer_position)


    def informUpCard(self,  auctionRound):
        
        if auctionRound == 1:
            print "The up card is"
            print self.upcard
        else:
            print "The up card was"
            print self.upcard
        

    def selectTrump(self):

        title = 'Please select the suit you would like to be trump:'
        options = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
        picker = Picker(options, title)
        choice, index = picker.start()
      
        title = 'Would you like to go alone?'
        options = ['Yes, alone', 'No, not alone']
        picker = Picker(options, title)
        alone, indexd = picker.start()

        Alone = alone == 'Yes, alone'
        suit = None
        if choice == 'Spades':
            suit = SUITS.spades
        elif choice == 'Hearts':
            suit = SUITS.hearts
        elif choice == 'Diamonds':
            suit = SUITS.diamonds
        elif choice == 'Clubs':
            suit = SUITS.clubs
        
        return BIDS[(suit, Alone)]

    def swapUpCard(self):
        
        raw_input("Press Enter to continue...")
        self.hand.append(self.upcard)
        trump_suit = self.upcard.getSuit()
        self.announceTrumpSuit(trump_suit)
        self.sortForPlay(trump_suit)

#        validCards = [[c.getSuit(),c.getRank()] for c in self.hand if self.isValidPlay(c, suitLed)]
        title = '%s has been selected as trump, and you got %s as the upcard. Select a card to return:' % (trump_suit, self.upcard)
        picker = Picker(self.hand, title)
        toReturn, index = picker.start()
        self.hand.remove(toReturn)

    def playCard(self, suitLed, trick):

        raw_input("Press Enter to continue...")
        validCards = [c for c in self.hand if self.isValidPlay(c, suitLed)]
        title = 'Here is the trick so far %s.\n Here is your remaining hand %s\n What card would you like to play? Here are your legal options:' % (self.convertTrickToText(trick), self.convertHandToText())
        picker = Picker(validCards, title)
        toPlay, index = picker.start()
        self.hand.remove(toPlay)
        return toPlay

    def announceBidMade(self, bid, player):
        
        if bid.getSuit() is not BIDS.passbid:
            self.announceTrumpSuit(bid.getSuit())
            self.sortForPlay(bid.getSuit())
        print "Player %s just bid %s" % (cardinalDirections[player], bid)
        
    def announceCardPlayed(self, card, player):

        print "Player %s just played %s" % (cardinalDirections[player], card)
        self.playToTrick += 1
        if self.playToTrick % 4 == 0:
            print "Next Trick:\n"

    def announceGameStart(self, hand, upcard, dealer, position):
        
        self.hand = hand
        self.upcard = upcard
        self.dealer = dealer
        self.position = position

        print "You are sitting in %s" % cardinalDirections[self.position]
        print "The dealer is in %s" % cardinalDirections[self.dealer]
        print "The upcard is %s" % self.upcard
        print "Your hand is %s" % self.convertHandToText()
        input = ("press any key to continue")

    def announceGameEnd(self, score):

        print "The hand is over.\n You got %d points." % score

    def isDealer(self):

        return self.position % 4 == self.dealer % 4

    def convertHandToText(self):
        
        text = ""
        for c in self.hand:
            text += "%s, " % c
        return text

    def convertTrickToText(self, trick):
        
        text = ""
        for c in trick:
            text += "%s, " % c
        return text
