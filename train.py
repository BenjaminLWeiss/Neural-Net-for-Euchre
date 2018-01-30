def train(numEpochs,filenames) :
	from computerPlayer import ComputerPlayer
	from euchreGameMaster import GameMaster
	from euchreGameMaster import POSITIONS

	p1 = ComputerPlayer()
	p1.load(filenames[0])
	p2 = ComputerPlayer()
	p2.load(filenames[1])
	p3 = ComputerPlayer()
	p3.load(filenames[2])
	p4 = ComputerPlayer()
	p4.load(filenames[3])

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

		p1.save(filenames[0])
		p2.save(filenames[1])
		p3.save(filenames[2])
		p4.save(filenames[3])

if __name__ == "__main__" :
	train(-1,['p1.mdl','p2.mdl','p3.mdl','p4.mdl'])

