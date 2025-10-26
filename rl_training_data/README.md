# RL Training Data Directory

This directory stores feedback data collected from users for Reinforcement Learning model improvement.

## Files

- **feedback_log.jsonl**: Line-delimited JSON file containing all user feedback entries
  - Each line is a complete JSON object with analysis data, user feedback, reward, and episode number
  - Format: `{"timestamp": "...", "analysis": {...}, "feedback": {...}, "reward": 10.0, "episode": 1}`

## Data Collection

The system collects 10-20 feedback samples before the RL agent starts learning patterns. After sufficient data is collected, the agent uses Experience Replay to train on historical feedback.

## Privacy

All data is stored locally. No data is sent to external servers.

## Backup

This directory should be backed up regularly as it contains the training history for the RL model.
