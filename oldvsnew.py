import computerLSTMPlayer
from euchreGameMaster import GameMaster

def doit() :
	print('Old models are N/S, new models are E/W')
	north = computerLSTMPlayer.ComputerPlayer()
	north.load('newermodels/p1_17000.mdl')
	south = computerLSTMPlayer.ComputerPlayer()
	south.load('newermodels/p3_17000.mdl')
	east = computerLSTMPlayer.ComputerPlayer(update_frequency=9999999)
	east.load('newermodels/p2_49500.mdl')
	west = computerLSTMPlayer.ComputerPlayer(update_frequency=9999999)
	west.load('newermodels/p3_49500.mdl')

	game = GameMaster(west,north,east,south)

	ns_score = 0
	for dealer in range(1000):
		ns_score += game.oneHand(dealer)
		if dealer % 10 == 0:
			print(ns_score)

	print('Old models scored %d'%ns_score)

if __name__ == '__main__' :
	doit()

