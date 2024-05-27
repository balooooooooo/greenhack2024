from flask import Flask, render_template, request
from dataset_parsing import Dataset

app = Flask(__name__)


dataset = Dataset('dataset.xlsx')


@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'datetime')
    if sort_by == 'kudos':
        ideas = dataset.sort_ideas_by_kudos()
    else:
        ideas = dataset.sort_ideas_by_datetime()

    ideas_info = [
        {
            'name': idea.name,
            'introduction': idea.introduction,
            'name_1': idea.name_1,
            'kudos': idea.kudos
        }
        for idea in ideas
    ]

    return render_template('idea_overview.html', ideas=ideas_info)


if __name__ == '__main__':
    app.run(debug=True)