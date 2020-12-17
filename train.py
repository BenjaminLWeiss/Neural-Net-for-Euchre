from computerLSTMPlayer import ComputerPlayer
from euchreGameMaster import GameMaster
from euchreGameMaster import POSITIONS
from random import shuffle
import os
import time

def load(player,filename) :
	try:
		player.load(filename)
	except FileNotFoundError:
		print("File %s not found, using random initialization"%filename)

def train(numEpochs,filenames) :
	p1 = ComputerPlayer()
	load(p1,filenames[0])
	p2 = ComputerPlayer()
	load(p2,filenames[1])
	p3 = ComputerPlayer()
	load(p3,filenames[2])
	p4 = ComputerPlayer()
	load(p4,filenames[3])

	players = [p1, p2, p3, p4]
	shuffle(players)

	game = GameMaster(players[0], players[1], players[2], players[3])

	# How many times around the table to play between saves
	saveFrequency = 40

	if numEpochs < 0 :
		numEpochs = 9999999999

	handCount = 0
	for i in range(numEpochs) :
		for j in range(saveFrequency) :
			game.oneHand(POSITIONS.north)
			game.oneHand(POSITIONS.east)
			game.oneHand(POSITIONS.south)
			game.oneHand(POSITIONS.west)
			handCount += 4
		
		print("Played %d hands at %s" % (handCount,time.ctime()))

		p1.save(filenames[0][:-4] + ('_%d.mdl' % handCount))
		p2.save(filenames[1][:-4] + ('_%d.mdl' % handCount))
		p3.save(filenames[2][:-4] + ('_%d.mdl' % handCount))
		p4.save(filenames[3][:-4] + ('_%d.mdl' % handCount))

if __name__ == "__main__" :
	train(-1,['p1.mdl','p2.mdl','p3.mdl','p4.mdl'])

