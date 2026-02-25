# Gymnasium Mode (Reinforcement Learning)

## 1. Overview
Gymnasium Mode transforms Serpentine into a headless simulation environment compatible with the standard `gymnasium` API. This allows training Reinforcement Learning (RL) agents using libraries like Stable-Baselines3, Ray RLLib, or CleanRL.

## 2. The Loop Difference
In this mode, the engine's `Tick` is driven manually by the external RL loop, not by an internal clock. `asyncio.sleep` is disabled to run as fast as possible.

## 3. Architecture: The Wrapper

The `SerpentineGymEnv` class acts as the bridge.

```python
class SerpentineGymEnv(gym.Env):
    def step(self, action):
        # 1. Convert RL Action to Engine Intent
        # 2. engine.tick()
        # 3. Extract Reward & ObservationComponent
        return obs, reward, terminated, truncated, info
```

## 4. Judging System (`EnvironmentJudgeSystem`)
This system is exclusive to Gym Mode. It is responsible for the "Rules of the Game".
*   **Input**: Physics events (Collisions) and Time.
*   **Logic**:
    *   Did the agent eat an apple? `Reward += 10`.
    *   Did the agent hit a wall? `Reward -= 10`, `Terminated = True`.
    *   Did time run out? `Truncated = True`.
*   **Output**: Updates the `RewardComponent`.

## 5. Mass Vectorization
Because Serpentine is ECS-based, we can spawn 1,000 agents in a single `World` instance. The `SerpentineGymEnv` can wrap this as a "Vector Environment", processing 1,000 actions in parallel within a single Python process, avoiding the overhead of `multiprocessing` usually required for Gym.
