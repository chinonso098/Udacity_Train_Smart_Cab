import random
import pygame 
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class QTable(object):
    def __init__(self):
        self.Q = dict()

    def getQValue(self, state, action):
        key = (state, action)
        return self.Q.get(key, None)

    def setQValue(self, state, action, q):
        key = (state, action)
        self.Q[key] = q

    def report(self):
        for k, v in self.Q.items():
            print k, v

class QLearn(Agent):
    def __init__(self):
        self.Q = QTable()       # Q(s, a)
        self.epsilon = .05      # probability of explore
        self.alpha   = .5      # learning rate
        self.gamma   = .9      # memory / discount factor of max Q(s',a')
        self.possible_actions = Environment.valid_actions

    def coinToss(self, p ):
        r = random.random()
        return r < p
 
    def exploitOrExploreAction(self, state):

        possible_actions = Environment.valid_actions
        action = None
        print possible_actions
        if (self.coinToss(self.epsilon)):
            print "explore"
            action = random.choice(possible_actions)
        else:
            print "exploit"
            best_qvalue = [self.Q.getQValue(state, action) for action in self.possible_actions]
            maxQ = max(best_qvalue)
            # if multiple actions are tied,randomly choose an action.
            if best_qvalue.count(maxQ) > 1: 
                # pick an action randomly from all max
                best_actions = [i for i in range(len(self.possible_actions)) if best_qvalue[i] == maxQ]                       
                action_temp = random.choice(best_actions)

            else:
                action_temp = best_qvalue.index(maxQ)
            action = self.possible_actions[action_temp]
        return action
 

    
    def updateQTable(self, state, action, reward, new_q):       
        best_qvalue = self.Q.getQValue(state, action)
        if best_qvalue is None:
            best_qvalue = reward
        else:
            best_qvalue += self.alpha * new_q 

        self.Q.setQValue(state, action, best_qvalue)

    def update(self, state, action, next_state, reward):
        best_qvalue = [self.Q.getQValue(next_state, a) for a in self.possible_actions]
        future_rewards = max(best_qvalue)         
        if future_rewards is None:
            future_rewards = 0.0
        old_qvalue = self.Q.getQValue(state, action)
        if old_qvalue is None:
            old_qvalue = 0.0
        
        self.updateQTable(state, action, reward, reward + self.gamma * future_rewards - old_qvalue)  
        #self.Q.report() ## Debug

class QLearningAgent(Agent):
    """An agent that learns to drive using Q-Learning"""

    def __init__(self, env):
        super(QLearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.possible_actions= Environment.valid_actions
        self.new_learner = QLearn()   
        self.counter = 0

    def reset(self, destination=None):
        self.planner.route_to(destination) 
        self.counter += 1

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self) 
        inputs = inputs.items()
        deadline = self.env.get_deadline(self)

        self.state = (inputs[0],inputs[1],inputs[3],self.next_waypoint)
                
        action = self.new_learner.exploitOrExploreAction(self.state)
        
        # Execute action and get reward
        reward = self.env.act(self, action)

        inputs2 = self.env.sense(self) 
        inputs2 = inputs2.items()
        next_state = (inputs2[0],inputs2[1],inputs2[3],self.next_waypoint)

        self.new_learner.update(self.state, action, next_state, reward)

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
        
        #print "LearningAgent.update(): iteration = {}, inputs = {}, waypoint = {} action = {}".format(self.counter, inputs, action, self.next_waypoint)  # [debug]
        #if self.counter >= 89:
            #outputData = open('C:\\Users\\chinonso\\Documents\\Udacity\\Train_Smart_Cab\\Smart_Cab\\smartcab\\smartcab\\result\\qlearning_log.txt', 'a')
            #outputData.write("LearningAgent.update(): iteration = {}, inputs = {}, waypoint = {} action = {}\n".format(self.counter, inputs, action, self.next_waypoint))
            #outputData.close()
            
        
        
def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(QLearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0.5, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False
    sim.run(n_trials=100)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()