from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

data = pd.read_csv("dataset.csv")
print(data)

class IdeaDataset:
    def __init__(self, path: str):

    """
    Load the entire dataset of the ideas
    """



@app.route('/')
def trending():
    # Example data, in real application fetch data from your source
    repos = [
        {"name": "THU-MIG/yolov10", "description": "YOLOv10: Real-Time End-to-End Object Detection", "stars": 2399, "stars_today": 331, "language": "Python", "built_by": ["user1", "user2", "user3"]},
        {"name": "khoj-ai/khoj", "description": "Your AI second brain.", "stars": 8716, "stars_today": 747, "language": "Python", "built_by": ["user4", "user5", "user6"]},
        {"name": "ente-io/ente", "description": "Fully open source, End to End Encrypted alternative to Google Photos.", "stars": 8423, "stars_today": 264, "language": "Dart", "built_by": ["user7", "user8", "user9"]},
    ]
    return render_template('idea_overview.html', repos=repos)

if __name__ == '__main__':
    app.run(debug=True)
