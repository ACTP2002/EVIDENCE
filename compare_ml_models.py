
import joblib

# Load and inspect new model
artifact = joblib.load("sentinel_model.pkl")
print("Keys:", artifact.keys())
print("Model type:", type(artifact["model"]))
print("Threshold:", artifact["threshold"])
print("Features:", artifact["features"])

# Load and inspect other model
other_artifact = joblib.load("behavior_iforest.pkl")
print("Keys:", other_artifact.keys())
print("Model type:", type(other_artifact["model"]))
print("Threshold:", other_artifact["threshold"])
# print("Features:", other_artifact["features"])