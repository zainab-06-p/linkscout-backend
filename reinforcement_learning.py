"""
🤖 REINFORCEMENT LEARNING SYSTEM FOR AI MISINFORMATION DETECTOR
===============================================================

This module implements a reinforcement learning system that:
1. Learns from user feedback (correct/incorrect detections)
2. Improves detection accuracy over time
3. Adapts to new misinformation patterns
4. Stores learning data for model improvement

Architecture:
- Q-Learning for decision making
- Experience Replay for stability
- Reward shaping based on user feedback
- Model fine-tuning using collected data
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import os
from collections import deque
import pickle

class ReinforcementLearningAgent:
    """
    Q-Learning based RL agent that learns optimal misinformation detection strategies
    """
    
    def __init__(self, state_size=10, action_size=5, learning_rate=0.001):
        """
        Initialize RL agent
        
        Args:
            state_size: Number of features in state representation
            action_size: Number of possible actions (detection confidence levels)
            learning_rate: Learning rate for Q-value updates
        """
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        
        # Q-table: state -> action values
        self.q_table = {}
        
        # Experience replay buffer
        self.memory = deque(maxlen=10000)
        
        # Learning statistics
        self.total_episodes = 0
        self.total_rewards = 0
        self.accuracy_history = []
        
        # Load existing model if available
        self.model_path = 'models_cache/rl_agent_model.pkl'
        self.load_model()
        
        print("🤖 [RL] Reinforcement Learning Agent initialized")
        print(f"   State size: {state_size}, Action size: {action_size}")
        print(f"   Learning rate: {learning_rate}, Gamma: {self.gamma}")
    
    def extract_features(self, analysis_data: Dict) -> np.ndarray:
        """
        Extract feature vector from analysis data
        
        Features:
        1. Misinformation percentage
        2. Number of suspicious items
        3. Average suspicion score
        4. Content length (normalized)
        5. Number of high-risk items
        6. Number of medium-risk items
        7. Number of low-risk items
        8. Sentiment score
        9. Source credibility
        10. Time of day (normalized)
        """
        features = np.zeros(self.state_size)
        
        try:
            # Feature 1: Misinformation percentage
            features[0] = analysis_data.get('misinformation_percentage', 0) / 100.0
            
            # Feature 2: Number of suspicious items
            suspicious_items = analysis_data.get('suspicious_items', [])
            features[1] = min(len(suspicious_items) / 10.0, 1.0)  # Normalize to 0-1
            
            # Feature 3: Average suspicion score
            if suspicious_items:
                scores = [item.get('score', 0) for item in suspicious_items]
                features[2] = np.mean(scores) / 100.0
            
            # Feature 4: Content length (normalized)
            content_length = len(analysis_data.get('content_preview', ''))
            features[3] = min(content_length / 10000.0, 1.0)
            
            # Feature 5-7: Count items by severity
            severity_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            for item in suspicious_items:
                severity = item.get('severity', 'LOW')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            features[4] = min(severity_counts['HIGH'] / 5.0, 1.0)
            features[5] = min(severity_counts['MEDIUM'] / 5.0, 1.0)
            features[6] = min(severity_counts['LOW'] / 5.0, 1.0)
            
            # Feature 8: Sentiment (derived from verdict)
            verdict = analysis_data.get('verdict', 'UNKNOWN')
            sentiment_map = {
                'HIGH RISK': 0.9,
                'MEDIUM RISK': 0.6,
                'LOW RISK': 0.3,
                'CREDIBLE': 0.1
            }
            features[7] = sentiment_map.get(verdict, 0.5)
            
            # Feature 9: Source credibility (derived from sources found)
            sources = analysis_data.get('sources_found', [])
            features[8] = min(len(sources) / 10.0, 1.0)
            
            # Feature 10: Time of day (might affect misinformation patterns)
            hour = datetime.now().hour
            features[9] = hour / 24.0
            
        except Exception as e:
            print(f"⚠️ [RL] Feature extraction error: {e}")
        
        return features
    
    def state_to_key(self, state: np.ndarray) -> str:
        """Convert state array to hashable key for Q-table"""
        # Discretize state to reduce Q-table size
        discretized = (state * 10).astype(int)
        return str(discretized.tolist())
    
    def choose_action(self, state: np.ndarray, explore=True) -> int:
        """
        Choose action using epsilon-greedy policy
        
        Actions:
        0 = Very Low Confidence (0-20%)
        1 = Low Confidence (20-40%)
        2 = Medium Confidence (40-60%)
        3 = High Confidence (60-80%)
        4 = Very High Confidence (80-100%)
        """
        if explore and np.random.random() < self.epsilon:
            # Exploration: random action
            return np.random.randint(0, self.action_size)
        
        # Exploitation: best known action
        state_key = self.state_to_key(state)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        
        return int(np.argmax(self.q_table[state_key]))
    
    def learn(self, state: np.ndarray, action: int, reward: float, 
              next_state: np.ndarray, done: bool):
        """
        Update Q-values using Q-learning algorithm
        
        Q(s,a) = Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
        """
        state_key = self.state_to_key(state)
        next_state_key = self.state_to_key(next_state)
        
        # Initialize Q-values if not exists
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.action_size)
        
        # Q-learning update
        current_q = self.q_table[state_key][action]
        
        if done:
            target_q = reward
        else:
            max_next_q = np.max(self.q_table[next_state_key])
            target_q = reward + self.gamma * max_next_q
        
        # Update Q-value
        self.q_table[state_key][action] += self.learning_rate * (target_q - current_q)
        
        # Store experience in replay buffer
        self.memory.append((state, action, reward, next_state, done))
        
        # Decay exploration rate
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        # Update statistics
        self.total_rewards += reward
        self.total_episodes += 1
    
    def calculate_reward(self, predicted_percentage: float, 
                        user_feedback: str, actual_percentage: float = 50.0) -> float:
        """
        Calculate reward based on user feedback
        
        Args:
            predicted_percentage: Model's prediction (0-100)
            user_feedback: 'correct', 'incorrect', 'partially_correct'
            actual_percentage: User-provided actual percentage (default 50.0)
        
        Returns:
            reward: Float value representing quality of prediction
        """
        if user_feedback == 'correct':
            # Perfect prediction
            return 10.0
        
        elif user_feedback == 'incorrect':
            # Wrong prediction - negative reward
            return -10.0
        
        elif user_feedback == 'partially_correct':
            # Somewhat correct
            if actual_percentage is not None and actual_percentage > 0:
                # Calculate error
                error = abs(predicted_percentage - actual_percentage)
                # Reward inversely proportional to error
                reward = 5.0 * (1.0 - error / 100.0)
                return max(reward, -5.0)
            return 2.0
        
        elif user_feedback == 'too_aggressive':
            # Model detected too much misinformation
            return -5.0
        
        elif user_feedback == 'too_lenient':
            # Model missed misinformation
            return -5.0
        
        return 0.0
    
    def process_feedback(self, analysis_data: Dict, user_feedback: Dict):
        """
        Process user feedback and update model
        
        Args:
            analysis_data: Original analysis result
            user_feedback: {
                'feedback_type': 'correct'|'incorrect'|'partially_correct',
                'actual_percentage': float (optional),
                'comments': str (optional)
            }
        """
        try:
            # Extract state from analysis
            state = self.extract_features(analysis_data)
            
            # Get predicted action (confidence level)
            predicted_percentage = analysis_data.get('misinformation_percentage', 0)
            action = int(predicted_percentage / 20)  # Convert to action (0-4)
            action = min(action, self.action_size - 1)
            
            # Calculate reward
            actual_pct = user_feedback.get('actual_percentage')
            if actual_pct is None:
                actual_pct = 50.0  # Default value
            
            reward = self.calculate_reward(
                predicted_percentage,
                user_feedback.get('feedback_type', 'correct'),
                float(actual_pct)
            )
            
            # Create next state (same as current for terminal state)
            next_state = state
            done = True
            
            # Update Q-values
            self.learn(state, action, reward, next_state, done)
            
            # Update accuracy history
            is_correct = reward > 0
            self.accuracy_history.append(is_correct)
            
            # Keep only last 100 for moving average
            if len(self.accuracy_history) > 100:
                self.accuracy_history.pop(0)
            
            # Save learning data
            self.save_feedback_data(analysis_data, user_feedback, reward)
            
            # Periodically save model
            if self.total_episodes % 10 == 0:
                self.save_model()
            
            print(f"✅ [RL] Feedback processed. Reward: {reward:.2f}, Epsilon: {self.epsilon:.3f}")
            print(f"   Total episodes: {self.total_episodes}, Avg reward: {self.total_rewards/max(self.total_episodes, 1):.2f}")
            
        except Exception as e:
            print(f"❌ [RL] Error processing feedback: {e}")
    
    def save_feedback_data(self, analysis_data: Dict, user_feedback: Dict, reward: float):
        """Save feedback data for future model training"""
        try:
            feedback_dir = 'rl_training_data'
            os.makedirs(feedback_dir, exist_ok=True)
            
            feedback_entry = {
                'timestamp': datetime.now().isoformat(),
                'analysis': analysis_data,
                'feedback': user_feedback,
                'reward': reward,
                'episode': self.total_episodes
            }
            
            # Append to JSONL file
            feedback_file = os.path.join(feedback_dir, 'feedback_log.jsonl')
            with open(feedback_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(feedback_entry) + '\n')
            
        except Exception as e:
            print(f"⚠️ [RL] Could not save feedback data: {e}")
    
    def get_statistics(self) -> Dict:
        """Get learning statistics"""
        accuracy = 0.0
        if self.accuracy_history:
            accuracy = sum(self.accuracy_history) / len(self.accuracy_history) * 100
        
        return {
            'total_episodes': self.total_episodes,
            'total_rewards': self.total_rewards,
            'average_reward': self.total_rewards / max(self.total_episodes, 1),
            'accuracy': accuracy,
            'epsilon': self.epsilon,
            'q_table_size': len(self.q_table),
            'memory_size': len(self.memory)
        }
    
    def save_model(self):
        """Save Q-table and statistics"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            model_data = {
                'q_table': self.q_table,
                'total_episodes': self.total_episodes,
                'total_rewards': self.total_rewards,
                'epsilon': self.epsilon,
                'accuracy_history': self.accuracy_history
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"💾 [RL] Model saved to {self.model_path}")
            
        except Exception as e:
            print(f"⚠️ [RL] Could not save model: {e}")
    
    def load_model(self):
        """Load Q-table and statistics"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.q_table = model_data.get('q_table', {})
                self.total_episodes = model_data.get('total_episodes', 0)
                self.total_rewards = model_data.get('total_rewards', 0)
                self.epsilon = model_data.get('epsilon', 1.0)
                self.accuracy_history = model_data.get('accuracy_history', [])
                
                print(f"📂 [RL] Model loaded from {self.model_path}")
                print(f"   Episodes: {self.total_episodes}, Accuracy: {sum(self.accuracy_history)/max(len(self.accuracy_history), 1)*100:.1f}%")
            
        except Exception as e:
            print(f"⚠️ [RL] Could not load model: {e}")
    
    def suggest_confidence_adjustment(self, analysis_data: Dict) -> Dict:
        """
        Use learned Q-values to suggest confidence adjustment
        
        Returns:
            {
                'original_percentage': float,
                'suggested_percentage': float,
                'confidence': float,
                'reasoning': str
            }
        """
        try:
            state = self.extract_features(analysis_data)
            action = self.choose_action(state, explore=False)
            
            # Map action to percentage range
            action_to_percentage = {
                0: 10,   # Very Low
                1: 30,   # Low
                2: 50,   # Medium
                3: 70,   # High
                4: 90    # Very High
            }
            
            suggested_percentage = action_to_percentage[action]
            original_percentage = analysis_data.get('misinformation_percentage', 0)
            
            # Calculate confidence based on Q-value
            state_key = self.state_to_key(state)
            if state_key in self.q_table:
                q_values = self.q_table[state_key]
                max_q = np.max(q_values)
                confidence = min(abs(max_q) / 10.0, 1.0)
            else:
                confidence = 0.5
            
            reasoning = self._generate_reasoning(original_percentage, suggested_percentage, action)
            
            return {
                'original_percentage': original_percentage,
                'suggested_percentage': suggested_percentage,
                'confidence': confidence,
                'reasoning': reasoning,
                'based_on_episodes': self.total_episodes
            }
            
        except Exception as e:
            print(f"❌ [RL] Error generating suggestion: {e}")
            return {
                'original_percentage': analysis_data.get('misinformation_percentage', 0),
                'suggested_percentage': analysis_data.get('misinformation_percentage', 0),
                'confidence': 0.0,
                'reasoning': 'RL agent unavailable'
            }
    
    def _generate_reasoning(self, original: float, suggested: float, action: int) -> str:
        """Generate human-readable reasoning for suggestion"""
        diff = suggested - original
        
        if abs(diff) < 5:
            return f"RL agent agrees with original assessment ({original}%)"
        elif diff > 0:
            return f"RL agent suggests higher suspicion (+{diff:.0f}% to {suggested}%) based on learned patterns"
        else:
            return f"RL agent suggests lower suspicion ({diff:.0f}% to {suggested}%) based on learned patterns"


# Global RL agent instance
rl_agent = None

def initialize_rl_agent():
    """Initialize global RL agent"""
    global rl_agent
    if rl_agent is None:
        rl_agent = ReinforcementLearningAgent(
            state_size=10,
            action_size=5,
            learning_rate=0.001
        )
    return rl_agent

def get_rl_agent():
    """Get or create RL agent"""
    global rl_agent
    if rl_agent is None:
        rl_agent = initialize_rl_agent()
    return rl_agent


if __name__ == '__main__':
    # Test RL agent
    print("Testing Reinforcement Learning Agent...")
    agent = ReinforcementLearningAgent()
    
    # Simulate some learning episodes
    for episode in range(5):
        # Fake analysis data
        analysis = {
            'misinformation_percentage': 75,
            'suspicious_items': [
                {'score': 80, 'severity': 'HIGH'},
                {'score': 60, 'severity': 'MEDIUM'}
            ],
            'verdict': 'HIGH RISK',
            'sources_found': ['source1', 'source2']
        }
        
        # Simulate different feedback types
        feedbacks = ['correct', 'incorrect', 'partially_correct']
        feedback = {
            'feedback_type': feedbacks[episode % len(feedbacks)],
            'actual_percentage': 70
        }
        
        agent.process_feedback(analysis, feedback)
    
    # Get statistics
    stats = agent.get_statistics()
    print("\nRL Agent Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Get suggestion
    suggestion = agent.suggest_confidence_adjustment(analysis)
    print("\nRL Suggestion:")
    for key, value in suggestion.items():
        print(f"  {key}: {value}")
