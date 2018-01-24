# This is a game master class for one hand of euchre
# It also makes the class of cards.
# It takes as inputs 4 players and their position, and the dealer's position. 
# 
# We use the eunm's at the top of the code for Suit, Rank, and Position encoding
# 



from random import shuffle as shuf

def enum(**named_values):
    return type('Enum', (), named_values)

SUITS = enum(HEART = 'heart', SPADE = 'spade', DIAMOND = 'diamond', CLUB = 'club', TRUMP = 'trump') 
# During play, the Trump suit will be entirely replaced by Trump (in addition to the Left) 

POSITIONS = enum(WEST = 0, NORTH = 1, EAST = 2, SOUTH = 3)
RANK = enum(NINE = 9, TEN = 10, JACK = 11, QUEEN = 12, KING = 13, ACE = 14, LEFT = 15, RIGHT = 16)
BIDS = enum(passbid = [None, None], hearts = [SUITS.HEART, False], heartsALONE = [SUITS.HEART, True], spades = [SUITS.SPADE, False], spadesALONE = [SUITS.SPADE, True], clubs = [SUITS.CLUB, False], clubsALONE = [SUITS.CLUB, True], diamonds = [SUITS.DIAMOND, False], diamondsALONE = [SUITS.DIAMOND, True])


class EuchreCard:
    # Holds [Suit, Rank] where Suit will be one of C, D, H, S, T and 
    # Rank is 9 through 14 for suits and 9 through 16 (skipping 11
    # for trump and 9 through 14 skipping 11 for non-trump same color)

    def __init__(self, suit, rank):
        if suit not in (SUITS.HEART, SUITS.SPADE, SUITS.DIAMOND, SUITS.CLUB, SUITS.TRUMP):
            print "Suit choice not valid"
        self.suit = suit
        if rank not in (RANK.NINE, RANK.TEN, RANK.JACK, RANK.QUEEN, RANK.KING, RANK.ACE, RANK.LEFT, RANK.RIGHT):
            print('Rank choice Not Valid')
        self.rank = rank

    def __str__(self):

        text_rank = None
        if self.rank == RANK.NINE:
            text_rank = 'Nine'
        elif self.rank == RANK.TEN:
            text_rank = 'Ten'
        elif self.rank == RANK.JACK: text_rank = 'Jack'
        elif self.rank == RANK.QUEEN: text_rank = 'Queen'
        elif self.rank == RANK.KING: text_rank = 'King'
        elif self.rank == RANK.ACE: text_rank = 'Ace'
        elif self.rank == RANK.LEFT: text_rank = 'Left'
        elif self.rank == RANK.RIGHT: text_rank = 'Right'
        return self.suit + " " + text_rank

    def getSuit(self): #Just for simplicity in reading
        return self.suit

    def getRank(self): #I know there are already functions for this
        return self.rank

    def declareTrump(self, suit): #This replaces the trump suit as Trump
        if self.suit == suit:
            self.suit = SUITS.TRUMP
            if self.rank == RANK.JACK:
                self.rank = RANK.RIGHT
        elif self.rank == RANK.JACK:
            if suit == SUITS.SPADE and self.suit == SUITS.CLUB:
                self.suit = SUITS.TRUMP
                self.rank = RANK.LEFT
            elif suit == SUITS.HEART and self.suit == SUITS.DIAMOND:
                self.suit = SUITS.TRUMP
                self.rank = RANK.LEFT
            elif suit == SUITS.DIAMOND and self.suit == SUITS.HEART:
                self.suit = SUITS.TRUMP
                self.rank = RANK.LEFT
            elif suit == SUITS.CLUB and self.suit == SUITS.SPADE:
                self.suit = SUITS.TRUMP
                self.rank = RANK.LEFT

    def scoreForBiddingRoundOne(self, suit):

        score = self.getRank()
        if self.getSuit() == suit:
            if score == 11: score += 5
            score += 20
        if score == 11:
            if suit == SUITS.SPADE and self.getSuit() == SUITS.CLUB:
                score += 24
            elif suit == SUITS.HEART and self.getSuit() == SUITS.DIAMOND:
                score += 24
            elif suit == SUITS.DIAMOND and self.getSuit() == SUITS.HEART:
                score += 24
            elif suit == SUITS.CLUB and self.getSuit() == SUITS.SPADE:
                score += 24

        return score

    def scoreForBiddingRoundTwo(self, suit):

        score = self.getRank()
        if self.getSuit() == suit:
            score -= 10
        if score == 11:
            score += 15

#        if suit == SUITS.SPADE and self.getSuit() == SUITS.CLUB:
#            score += 10
#        elif suit == SUITS.HEART and self.getSuit() == SUITS.DIAMOND:
#            score += 10
#        elif suit == SUITS.DIAMOND and self.getSuit() == SUITS.HEART:
#            score += 10
#        elif suit == SUITS.CLUB and self.getSuit() == SUITS.SPADE:
#            score += 10


        return score

    def scoreForPlay(self, suit):

        score = self.getRank()
        if self.getSuit() == SUITS.TRUMP:
            score += 10
        
        if self.getSuit() == SUITS.SPADE and suit == SUITS.CLUB:
            score -= 2
        elif self.getSuit() == SUITS.HEART and suit == SUITS.DIAMOND:
            score -= 2
        elif self.getSuit() == SUITS.DIAMOND and suit == SUITS.HEART:
            score -= 2
        elif self.getSuit() == SUITS.CLUB and suit == SUITS.SPADE:
            score -= 2

        return score


class Call: #This class is for calls made during the auction

    def __init__(self, bid):
        suit = bid[0]
        alone = bid[1]
        if suit is not None and suit not in (SUITS.SPADE, SUITS.HEART, SUITS.DIAMOND, SUITS.CLUB):
            print('Bid Suit Not Valid')
        self.suit = suit
        if alone is not None and alone not in (False, True):
            print('Alone Call not True/False')
        self.alone = alone

    def __repr__(self):
        
        bid = None
        alone = None
        if self.getSuit() is None:
            bid = 'Pass'
            return bid
        else:
            if self.goAlone():
                alone = 'Alone'
            else: alone = ''
            return str(self.getSuit()) + alone
    
    def getSuit(self):
        return self.suit

    def goAlone(self):
        return self.alone

class GameMaster:

    def __init__(self, PlayerWest, PlayerNorth, PlayerEast, PlayerSouth):

        self.South = PlayerSouth
        self.West = PlayerWest
        self.North = PlayerNorth
        self.East = PlayerEast
    
        self.Play_Order = [self.West, self.North, self.East, self.South] #Keeps a mod 4 play order

    def fullGame(self):

        NS_score = 0
        EW_score = 0
        Dealer = 2
        while NS_score < 10 and EW_score < 10:
            Dealer = (Dealer + 1) % 4
            handScore = self.oneHand(Dealer)
            if handScore > 0:
                NS_score += handScore
            else:
                EW_score -= handScore
            print 'Current score is N/S: %r \n and E/W: %r' % (NS_score, EW_score)

        print 'North/South score = %r \n East/West score = %r' % (NS_score, EW_score)
        return NS_score, EW_score

    def oneHand(self, Dealer_Position): #This function plays one hand with the players and the given dealer. 

        Dealer_Position = Dealer_Position % 4
        Deck = self.resetDeck() # rebuilds a Euchre Deck and shuffles
        UpCard = self.dealCards(Deck, Dealer_Position) # passes the hands and upcard to the players, saves
        # Upcard for future use in auction

        Bid, Declarer = self.auction(UpCard, Dealer_Position)
        Trick_Leader, Skipped_Player, NS_Trick_Total, EW_Trick_Total = self.readyTrickOne(Bid, Declarer, Dealer_Position)
        Game_Over = False
        
        while Game_Over == False:
            Trick = self.oneTrick(Skipped_Player, Trick_Leader)
            Trick_Winner = self.trickWinner(Trick)
            NS_Trick_Total, EW_Trick_Total = self.trickTotal(Trick_Leader, Trick_Winner, NS_Trick_Total, EW_Trick_Total)
            Game_Over, NS_score = self.gameOver(NS_Trick_Total, EW_Trick_Total, Declarer, Bid.goAlone())
            Trick_Leader = self.newLeader(Trick_Leader, Trick_Winner)
        
        return NS_score


    def oneTrick(self, Skipped_Player, Trick_Leader):
# Begins cardplay round

        Trick = [None, None, None, None] # Stores the 4 cards in the trick
        Suit_Led = None
        for turn in xrange(4): # turn is for turn to play in the trick
            Player_Turn = (Trick_Leader + turn) % 4 
            To_Play = self.Play_Order[Player_Turn].playCard(Suit_Led, Trick)
                #To_Play.declareTrump(Bid.getSuit()) This line can be uncommented if you are worried
                # The players are not correctly setting Trump
            if Player_Turn == Skipped_Player:
                To_Play = None
            
            Trick[turn] = To_Play
            Suit_Led = Trick[0].getSuit()
            for x in self.Play_Order:
                x.announceCardPlayed(To_Play, Player_Turn)
        return Trick

            # We now calculate which card played wins the trick
            # This is stored by index of the card in Trick

    def readyTrickOne(self, Bid, Declarer, Dealer_Position):
        Trick_Leader = (Dealer_Position + 1) % 4
        if Bid.goAlone():
            Skipped_Player = (Declarer + 2 )% 4
            if Skipped_Player == Trick_Leader:
                Trick_Leader += 1
        else: Skipped_Player = None
        return Trick_Leader, Skipped_Player, 0, 0


    def newLeader(self, Trick_Leader, winning_index):

        return (Trick_Leader + winning_index) % 4

    def trickWinner(self, Trick):
        winning_index = None
        Trump_Played = False
        for c in Trick:
            if c is not None:
                if c.getSuit() == SUITS.TRUMP:
                    Trump_Played = True
        
        if Trump_Played:
            for x in xrange(4):
                if Trick[x] is not None:
                    if Trick[x].getSuit() == SUITS.TRUMP:
                        if winning_index is not None:
                            if Trick[x].getRank() > Trick[winning_index].getRank():
                                winning_index = x
                        else:
                            winning_index = x
        else:
            winning_index = 0
            for x in xrange(1,4):
                if Trick[x] is not None:
                    if Trick[x].getSuit() == Trick[0].getSuit():
                        if Trick[x].getRank() > Trick[winning_index].getRank():
                            winning_index = x
                            
        return winning_index
    ## W/E = 0/2 and N/S = 1/3
            # Now we score the trick for the winning pair.
      
    def trickTotal(self, Trick_Leader, winning_index, NS_Trick_Total, EW_Trick_Total):
        if (Trick_Leader + winning_index) % 2 == 0:
            EW_Trick_Total += 1
        else:
            NS_Trick_Total += 1

        return NS_Trick_Total, EW_Trick_Total
            # Determine the leader for the next trick
            #Trick_Leader = (Trick_Leader + winning_index) % 4

    def gameOver(self, NS_Trick_Total, EW_Trick_Total, Declarer, Alone):
            # Check if the trick totals mean the score has been determined
        if Declarer % 2 == 0:
            if NS_Trick_Total > 2:
                self.returnScore(2)
                return True, 2
            elif EW_Trick_Total == 5:
                self.returnScore(-2 - Alone*2)
                return True, -2 - Alone*2
            elif EW_Trick_Total > 2 and NS_Trick_Total > 0:
                self.returnScore(-1)
                return True, -1
            else: return False, 0
        else:
            if EW_Trick_Total > 2:
                self.returnScore(-2)
                return True, -2
            elif NS_Trick_Total == 5:
                self.returnScore(2 + Alone*2)
                return True, 2 + Alone*2
            elif NS_Trick_Total > 2 and EW_Trick_Total > 0:
                self.returnScore(1)
                return True, 1
            else: return False, 0

    def returnScore(self, score):

        self.Play_Order[1].announceGameEnd(score)
        self.Play_Order[3].announceGameEnd(score)
        self.Play_Order[0].announceGameEnd(-score)
        self.Play_Order[2].announceGameEnd(-score)

    def resetDeck(self):
        
        NewDeck = [] #Initializes deck
        for s in [SUITS.SPADE, SUITS.HEART, SUITS.DIAMOND, SUITS.CLUB]:
            for r in xrange(9, 15):
                NewDeck.append(EuchreCard(s, r))

        shuf(NewDeck) #Shuffles deck
        return NewDeck

    def dealCards(self, Deck, Dealer_Position):

        WestHand = Deck[0:5] #Deals deck
        NorthHand = Deck[5:10]
        EastHand = Deck[10:15]
        SouthHand = Deck[15:20]
        UpCard = Deck[20]

        print UpCard

        ## Tells players their hands and upcard
        self.West.announceGameStart(WestHand, UpCard, Dealer_Position, 0)
        self.North.announceGameStart(NorthHand, UpCard, Dealer_Position, 1)
        self.East.announceGameStart(EastHand, UpCard, Dealer_Position, 2)
        self.South.announceGameStart(SouthHand, UpCard, Dealer_Position, 3)
        return UpCard

    def auction(self, UpCard, Dealer_Position):

        Bid_made = False
        Player_Turn = (Dealer_Position + 1) % 4
        Bid = Call([None, None])
        Declarer = None
        Number_of_Passes = 0
        auctionRound = 0

        while Bid_made == False:
            if Number_of_Passes < 4:
                auctionRound = 0
            else: auctionRound = 1

            Bid = self.Play_Order[Player_Turn].makeBid(auctionRound, UpCard, Dealer_Position)
            if Bid.getSuit() is None:

                if Number_of_Passes == 7: # Forces Dealer to Bid Spades or Hearts
                    if UpCard.getSuit() == SUITS.HEART:
                        Bid = Call([SUITS.SPADE, False])
                    else: Bid = Call([SUITS.HEART, False])
                    Bid_made = True
                    Declarer = Player_Turn
                    '''for c in Deck:
                        c.declareTrump(Bid.getSuit())'''
                    # The players should be running the above for loop on their own

                for x in self.Play_Order:
                    x.announceBidMade(Bid, Player_Turn)
                Player_Turn = (Player_Turn + 1) % 4
                Number_of_Passes += 1

            else:
                if auctionRound == 0 and Bid.getSuit() != UpCard.getSuit():
                    # Forces players to bid only upcard suit 1st round
                    Bid = Call([None, None])
                    Number_of_Passes += 1
                elif auctionRound == 1 and Bid.getSuit() == UpCard.getSuit():
                    # Prevents players from bidding upcard suit 2nd round
                    Bid = Call([None, None])
                    Number_of_Passes += 1
                for x in self.Play_Order:
                    x.announceBidMade(Bid, Player_Turn)
                if Bid.getSuit() is not None:
                    Declarer = Player_Turn
                    Bid_made = True
                    if auctionRound == 0:
                        self.Play_Order[Dealer_Position].swapUpCard()
                    
                    '''for c in Deck:
                        c.declareTrump(Bid.getSuit())
                    Bid_made = True'''
                    # The players should be running the above for loop on their own
        return Bid, Declarer
