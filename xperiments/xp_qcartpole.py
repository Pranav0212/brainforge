from collections import deque

import numpy as np
import gym

from brainforge import BackpropNetwork
from brainforge.layers import DenseLayer, ClockworkLayer
from brainforge.optimization import RMSprop
from brainforge.reinforcement import AgentConfig
from reinforcement.qlearning import DDQN as AgentType
from matplotlib import pyplot

env = gym.make("CartPole-v1")
nactions = env.action_space.n


def QannRecurrent():
    brain = BackpropNetwork(env.observation_space.shape, layers=[
        ClockworkLayer(120, activaton="tanh"),
        DenseLayer(60, activation="relu"),
        DenseLayer(nactions, activation="linear")
    ], cost="mse", optimizer=RMSprop(eta=0.0001))
    return brain


def QannDense():
    brain = BackpropNetwork(input_shape=env.observation_space.shape, layerstack=[
        DenseLayer(24, activation="tanh"),
        DenseLayer(nactions, activation="linear")
    ], cost="mse", optimizer=RMSprop(eta=0.0001))
    return brain


def run(agent):
    episode = 1
    rewards = deque(maxlen=100)

    while 1:
        state = env.reset()
        win = False
        steps = 1
        reward = None
        for step in range(200):
            action = agent.sample(state, reward)
            state, reward, done, info = env.step(action)
            if done:
                break
        else:
            win = True

        rewards.append(steps)
        cost = agent.accumulate(state, 10. if win else -1.)
        meanrwd = np.mean(rewards)
        print(f"\rEpisode {episode:>6}, running reward: {meanrwd:.2f}, Cost: {cost:>6.4f}",
              end="")
        if win:
            print(" Win!")
        episode += 1


def plotrun(agent):
    rewards = []
    rwmean = []
    EPISODES = 1000
    for episode in range(1, EPISODES + 1):
        state = env.reset()
        reward_sum = 0.
        reward = 0.
        win = False
        for time in range(1, 151):
            action = agent.sample(state, reward)
            state, reward, done, info = env.step(action)
            reward_sum += reward
            if done:
                break
        else:
            win = True
        rewards.append(reward_sum)
        rwmean.append(np.mean(rewards[-10:]))
        cost = agent.accumulate(state, (-1. if not win else 1.))
        print(f"\r{episode / EPISODES:.1%}, Cost: {cost:8>.4f}, Epsilon: {agent.cfg.epsilon:8.6f}", end="")
    print()
    Xs = np.arange(len(rewards))
    pyplot.scatter(Xs, rewards, marker=".", s=3, c="r", alpha=0.5)
    pyplot.plot(Xs, rwmean, color="b", linewidth=2)
    pyplot.show()


if __name__ == '__main__':
    run(AgentType(QannDense(), nactions, AgentConfig(
        epsilon_greedy_rate=1.0, epsilon_decay_factor=0.9998, epsilon_min=0.0,
        discount_factor=0.6, replay_memory_size=7200, training_batch_size=720,
    )))
