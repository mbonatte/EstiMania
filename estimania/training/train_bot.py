import os
import time
import pickle
import random
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

from estimania.features import FEATURE_NAMES
from estimania.training.simulation import simulate_single_round

from multiprocessing import Pool

class CustomMLPModel:
    """Pure numpy forward pass matching sklearn MLPRegressor with ReLU activations."""
    def __init__(self, coefs, intercepts):
        self.coefs_ = coefs
        self.intercepts_ = intercepts

    def predict(self, X):
        X_arr = np.array(X, dtype=np.float32)
        layer_input = X_arr
        for i in range(len(self.coefs_) - 1):
            layer_input = np.maximum(0, np.dot(layer_input, self.coefs_[i]) + self.intercepts_[i])
        output = np.dot(layer_input, self.coefs_[-1]) + self.intercepts_[-1]
        return output.flatten()

def _worker_sim_round(args):
    bet_policy_model, seed = args
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    player_counts = [2, 3, 4, 5]
    n_players = random.choice(player_counts)
    max_c = min(8, 52 // n_players)
    n_cards = random.randint(1, max_c)
    return simulate_single_round(
        num_players=n_players,
        n_cards=n_cards,
        bet_policy_model=bet_policy_model,
    )

def generate_dataset(num_rounds: int, bet_policy_model=None, verbose: bool = True, workers: int = 6):
    """
    Generate dataset of feature vectors and rewards from simulated rounds using worker pool.
    """
    if verbose:
        print(f"Generating data from {num_rounds} simulated rounds with {workers} workers...")
    start_time = time.time()

    seeds = [random.randint(0, 1000000000) for _ in range(num_rounds)]
    tasks = [(bet_policy_model, s) for s in seeds]

    all_X = []
    all_y = []

    if workers > 1:
        with Pool(processes=workers) as pool:
            for i, samples in enumerate(pool.imap_unordered(_worker_sim_round, tasks, chunksize=25)):
                for feats, reward in samples:
                    all_X.append(feats)
                    all_y.append(reward)
                if verbose and (i + 1) % 2000 == 0:
                    elapsed = time.time() - start_time
                    print(f"  Completed {i + 1}/{num_rounds} rounds ({len(all_X)} samples) in {elapsed:.1f}s")
    else:
        for r in range(num_rounds):
            samples = _worker_sim_round(tasks[r])
            for feats, reward in samples:
                all_X.append(feats)
                all_y.append(reward)
            if verbose and (r + 1) % 2000 == 0:
                elapsed = time.time() - start_time
                print(f"  Completed {r + 1}/{num_rounds} rounds ({len(all_X)} samples) in {elapsed:.1f}s")

    if verbose:
        total_time = time.time() - start_time
        print(f"Data generation complete: {len(all_X)} samples in {total_time:.2f}s")

    return np.array(all_X, dtype=np.float32), np.array(all_y, dtype=np.float32)

def train_and_export(
    num_rounds_phase1: int = 5000,
    num_rounds_phase2: int = 5000,
    export_path: str = None,
):
    if export_path is None:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        export_path = os.path.join(current_dir, 'trained_bot_model.pkl')

    print("=== Phase 1: Exploration & Bootstrap Training ===")
    X1, y1 = generate_dataset(num_rounds_phase1, bet_policy_model=None, workers=6)

    mlp = MLPRegressor(
        hidden_layer_sizes=(128, 64, 32),
        activation='relu',
        solver='adam',
        alpha=1e-4,
        learning_rate_init=0.002,
        max_iter=150,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
    )

    print("Training Phase 1 MLP model...")
    mlp.fit(X1, y1)
    train_pred = mlp.predict(X1)
    print(f"Phase 1 - Train MSE: {mean_squared_error(y1, train_pred):.4f}, R2: {r2_score(y1, train_pred):.4f}")

    phase1_model = CustomMLPModel(mlp.coefs_, mlp.intercepts_)

    print("\n=== Phase 2: Self-Play Reinforcement Training ===")
    X2, y2 = generate_dataset(num_rounds_phase2, bet_policy_model=phase1_model, workers=6)

    # Combine datasets
    X_combined = np.vstack([X1, X2])
    y_combined = np.concatenate([y1, y2])

    X_train, X_test, y_train, y_test = train_test_split(
        X_combined, y_combined, test_size=0.15, random_state=42
    )

    print(f"Final training set size: {len(X_train)} samples, Test set size: {len(X_test)} samples")
    final_mlp = MLPRegressor(
        hidden_layer_sizes=(128, 64, 32),
        activation='relu',
        solver='adam',
        alpha=1e-4,
        learning_rate_init=0.0015,
        max_iter=250,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
    )
    final_mlp.fit(X_train, y_train)

    test_pred = final_mlp.predict(X_test)
    mse = mean_squared_error(y_test, test_pred)
    r2 = r2_score(y_test, test_pred)
    print(f"Final Grandmaster Model Evaluation - Test MSE: {mse:.4f}, Test R2: {r2:.4f}")

    # Export weights for CustomMLPRegressor
    export_data = {
        'features': FEATURE_NAMES,
        'coefs': final_mlp.coefs_,
        'intercepts': final_mlp.intercepts_,
    }

    with open(export_path, 'wb') as f:
        pickle.dump(export_data, f)

    print(f"Grandmaster model exported successfully to: {export_path}")
    return export_path

if __name__ == '__main__':
    train_and_export()
