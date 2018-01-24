#from __future__ import print_function
import curses
from euchreGameMaster import SUITS
from euchreGameMaster import POSITIONS
from euchreGameMaster import RANK
from euchreGameMaster import EuchreCard
from euchreGameMaster import Call
from euchreGameMaster import GameMaster 
from player import Player
from pick import Picker

#def go_back(picker):
#    return (None, -1)


def enum(**named_values):
    return type('Enum', (), named_values)

BIDS = enum(passbid = [None, None], hearts = [SUITS.HEART, False], heartsALONE = [SUITS.HEART, True], spades = [SUITS.SPADE, False], spadesALONE = [SUITS.SPADE, True], clubs = [SUITS.CLUB, False], clubsALONE = [SUITS.CLUB, True], diamonds = [SUITS.DIAMOND, False], diamondsALONE = [SUITS.DIAMOND, True])


class Human(Player):

    def makeBid(self, auctionRound):
        
        raw_input("Press Enter to continue...")
#        self.informUpCard(auctionRound)
        if auctionRound == 0:
            self.sortForBiddingRoundOne(self.upcard.getSuit())
            title = 'The upcard is %r. \n Your hand is %r. \n Would you like to Bid, or Pass?' % (self.upcard, self.hand)
        else:
            self.sortForBiddingRoundTwo(self.upcard.getSuit())
            title = 'The upcard was %r. \n Your hand is %r. \n Would you like to Bid, or Pass?' % (self.upcard, self.hand)
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
                return self.makeBid(auctionRound)
            
        elif option == 'Pass':
            if self.isValidBid(Call(BIDS.passbid), self.upcard, auctionRound):
                return Call(BIDS.passbid)
            else:
                print "You may not passout the hand"
                return self.makeBid(auctionRound)


    def informUpCard(self,  auctionRound):
        
        if auctionRound == 1:
            print "The up card is"
            self.upcard
        else:
            print "The up card was"
            self.upcard
        

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
            suit = SUITS.SPADE
        elif choice == 'Hearts':
            suit = SUITS.HEART
        elif choice == 'Diamonds':
            suit = SUITS.DIAMOND
        elif choice == 'Clubs':
            suit = SUITS.CLUB
        
        return Call([suit, Alone])

    def swapUpCard(self):
        
        raw_input("Press Enter to continue...")
        self.hand.append(self.upcard)
        trump_suit = self.upcard.getSuit()
        self.announceTrumpSuit(trump_suit)
        self.sortForPlay(trump_suit)

#        validCards = [[c.getSuit(),c.getRank()] for c in self.hand if self.isValidPlay(c, suitLed)]
        title = '%r has been selected as trump, and you got %r as the upcard. Select a card to return:' % (trump_suit, self.upcard)
        picker = Picker(self.hand, title)
        toReturn, index = picker.start()
        self.hand.remove(toReturn)

    def playCard(self, suitLed, trick):

        raw_input("Press Enter to continue...")
        validCards = [c for c in self.hand if self.isValidPlay(c, suitLed)]
        title = 'Here is the trick so far %r.\n Here is your remaining cards %r\n What card would you like to play? Here are your legal options:' % (trick, self.hand)
        picker = Picker(validCards, title)
        toPlay, index = picker.start()
        self.hand.remove(toPlay)
        return toPlay

    def announceBidMade(self, bid, player):
        
        if bid.getSuit() is not BIDS.passbid:
            self.announceTrumpSuit(bid.getSuit())
            self.sortForPlay(bid.getSuit())
        print "Player %r just bid %r" % (player, bid)
        
    def announceCardPlayed(self, card, player):

        print "Player %r just played %r" % (player, card)

    def announceGameStart(self, hand, upcard, dealer, position):
        
        self.hand = hand
        self.upcard = upcard
        self.dealer = dealer
        self.position = position

        print "You are sitting in %r" % self.position
        print "The dealer is in %r" % self.dealer
        print "The upcard is %r" % self.upcard
        print "Your hand is %r" % self.hand
        input = ("press any key to continue")

    def announceGameEnd(self, score):

        print "The hand is over.\n You got %d points." % score

    def isDealer(self):

        return self.position % 4 == self.dealer % 4
