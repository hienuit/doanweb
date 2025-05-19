from flask import Blueprint, request, jsonify
import numpy as np
import tensorflow as tf

federated_blueprint = Blueprint('federated', __name__)

# ----------------------------
# ENCODING & MAPPING
# ----------------------------
mood_map = {"chill": 0, "active": 1, "adventure": 2, "relaxed": 3}
place_map = {"river": 0, "mountain": 1, "quiet": 2, "city": 3, "beach": 4}
location_map = {"south": 0, "north": 1, "central": 2}
reverse_location_map = {v: k for k, v in location_map.items()}

# ----------------------------
# SERVER TRAINING DATA
# ----------------------------
raw_data = [
    ["chill", "river", "south"],
    ["active", "mountain", "north"],
    ["adventure", "quiet", "central"],
    ["chill", "quiet", "south"],
    ["active", "river", "north"],
    ["adventure", "mountain", "central"],
    ["chill", "river", "south"],
    ["active", "quiet", "north"],
    ["adventure", "mountain", "central"],
    ["chill", "quiet", "south"]
]

X = np.array([[mood_map[row[0]], place_map[row[1]]] for row in raw_data])
y = tf.keras.utils.to_categorical([location_map[row[2]] for row in raw_data], num_classes=3)

# ----------------------------
# GLOBAL MODEL & STATE
# ----------------------------
global_weights = []

def create_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(2,)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(3, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

model = create_model()
model.fit(X, y, epochs=50, verbose=0)

# ----------------------------
# ROUTES
# ----------------------------

@federated_blueprint.route('/upload_weights', methods=['POST'])
def upload_weights():
    try:
        data = request.get_json()

        if 'weights' not in data:
            return jsonify({"status": "error", "message": "Missing 'weights' field"}), 400

        client_weights = [np.array(w) for w in data['weights']]
        global_weights.append(client_weights)
        print(f"[SERVER] Received weights from client #{len(global_weights)}")

        # Calculate average weights immediately
        if global_weights:
            avg_weights = [np.mean(w, axis=0) for w in zip(*global_weights)]
            model.set_weights(avg_weights)
            global_weights.clear()  # clear after update

            # Evaluate updated model
            loss, acc = model.evaluate(X, y, verbose=0)
            print(f"[SERVER] Updated model - Loss: {loss:.4f}, Accuracy: {acc:.4f}")

        return jsonify({
            "status": "received",
            "message": "Weights updated successfully.",
            "accuracy": float(acc)
        })

    except Exception as e:
        print(f"[SERVER] Error in upload_weights: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@federated_blueprint.route('/get_weights', methods=['GET'])
def get_weights():
    print("[SERVER] Client requested weights")
    return jsonify([w.tolist() for w in model.get_weights()])

