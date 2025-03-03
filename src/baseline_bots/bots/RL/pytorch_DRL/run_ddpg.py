import sys

import gym
import matplotlib.pyplot as plt
import numpy as np
from common.utils import agg_double_list
from DDPG import DDPG

MAX_EPISODES = 5000
EPISODES_BEFORE_TRAIN = 100
EVAL_EPISODES = 10
EVAL_INTERVAL = 100

# max steps in each episode, prevent from running too long
MAX_STEPS = 10000  # None

MEMORY_CAPACITY = 10000
BATCH_SIZE = 100
CRITIC_LOSS = "mse"
MAX_GRAD_NORM = None

TARGET_UPDATE_STEPS = 5
TARGET_TAU = 0.01

REWARD_DISCOUNTED_GAMMA = 0.99

EPSILON_START = 0.99
EPSILON_END = 0.05
EPSILON_DECAY = 500

DONE_PENALTY = None

RANDOM_SEED = 2017


def run(env_id="Pendulum-v0"):

    env = gym.make(env_id)
    env.seed(RANDOM_SEED)
    env_eval = gym.make(env_id)
    env_eval.seed(RANDOM_SEED)
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.shape[0]

    ddpg = DDPG(
        env=env,
        memory_capacity=MEMORY_CAPACITY,
        state_dim=state_dim,
        action_dim=action_dim,
        batch_size=BATCH_SIZE,
        max_steps=MAX_STEPS,
        done_penalty=DONE_PENALTY,
        target_update_steps=TARGET_UPDATE_STEPS,
        target_tau=TARGET_TAU,
        reward_gamma=REWARD_DISCOUNTED_GAMMA,
        critic_loss=CRITIC_LOSS,
        epsilon_start=EPSILON_START,
        epsilon_end=EPSILON_END,
        epsilon_decay=EPSILON_DECAY,
        max_grad_norm=MAX_GRAD_NORM,
        episodes_before_train=EPISODES_BEFORE_TRAIN,
    )

    episodes = []
    eval_rewards = []
    while ddpg.n_episodes < MAX_EPISODES:
        ddpg.interact()
        if ddpg.n_episodes >= EPISODES_BEFORE_TRAIN:
            ddpg.train()
        if ddpg.episode_done and ((ddpg.n_episodes + 1) % EVAL_INTERVAL == 0):
            rewards, _ = ddpg.evaluation(env_eval, EVAL_EPISODES)
            rewards_mu, rewards_std = agg_double_list(rewards)
            print(
                "Episode: %d, Average Reward: %.5f" % (ddpg.n_episodes + 1, rewards_mu)
            )
            episodes.append(ddpg.n_episodes + 1)
            eval_rewards.append(rewards_mu)

    episodes = np.array(episodes)
    eval_rewards = np.array(eval_rewards)
    np.savetxt("./output/%s_ddpg_episodes.txt" % env_id, episodes)
    np.savetxt("./output/%s_ddpg_eval_rewards.txt" % env_id, eval_rewards)

    plt.figure()
    plt.plot(episodes, eval_rewards)
    plt.title("%s" % env_id)
    plt.xlabel("Episode")
    plt.ylabel("Average Reward")
    plt.legend(["DDPG"])
    plt.savefig("./output/%s_ddpg.png" % env_id)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        run(sys.argv[1])
    else:
        run()
