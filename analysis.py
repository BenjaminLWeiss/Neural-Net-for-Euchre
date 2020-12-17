import computerLSTMPlayer
import torch
from torch.nn.functional import softmax
from computerLSTMPlayer import all_actions

p = computerLSTMPlayer.ComputerPlayer()
p.load('newermodels/p1_49500.mdl')

transcript = p.brain.memory[0]

embeddings = torch.unsqueeze(p.brain.embedding(transcript),1)
predictions = p.brain.output(p.brain.lstm(embeddings,(p.brain.h0,p.brain.c0))[0])
play_predictions = softmax(predictions[5:-1,0,:],dim=-1)
indices = torch.argsort(play_predictions) 

for i in range(play_predictions.size(0)):
	for j in range(-10,-1):
		index = indices[i,j]
		print(play_predictions[i,index].item(), all_actions[index], all_actions[transcript[i+6]])
	print('==============================')

