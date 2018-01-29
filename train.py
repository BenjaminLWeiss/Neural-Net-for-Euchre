def train(numEpochs) :
	from computerPlayer import ComputerPlayer
	from euchreGameMaster import GameMaster
	from euchreGameMaster import POSITIONS

	p1 = ComputerPlayer()
	p2 = ComputerPlayer()
	p3 = ComputerPlayer()
	p4 = ComputerPlayer()

	game = GameMaster(p1,p2,p3,p4)

	# How many times around the table to play between saves
	saveFrequency = 10

	if numEpochs < 0 :
		numEpochs = 9999999999

	handCount = 0
	for i in xrange(numEpochs) :
		for j in xrange(saveFrequency) :
			game.oneHand(POSITIONS.north)
			game.oneHand(POSITIONS.east)
			game.oneHand(POSITIONS.south)
			game.oneHand(POSITIONS.west)
			handCount += 4
		
		print "Played %d hands" % handCount

		p1.save('p1.mdl')
		p2.save('p2.mdl')
		p3.save('p3.mdl')
		p4.save('p4.mdl')

if __name__ == "__main__" :
	train(-1)

