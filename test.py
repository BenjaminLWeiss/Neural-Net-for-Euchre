from computerLSTMPlayer import ComputerPlayer
from humanPlayer import HumanPlayer
from euchreGameMaster import GameMaster

def doit() :
	p1 = ComputerPlayer()
	p1.load('p1_17000_3200.mdl')
	p2 = ComputerPlayer()
	p2.load('p2_17000_3200.mdl')
	p3 = ComputerPlayer()
	p3.load('p3_17000_3200.mdl')
	p4 = HumanPlayer()

	game = GameMaster(p1,p2,p3,p4)

	game.fullGame()

if __name__ == '__main__' :
	doit()
