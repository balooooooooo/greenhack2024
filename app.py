from flask import Flask, render_template, request, redirect, url_for
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
            'idea_id': idea.idea_id,
            'name': idea.name,
            'introduction': idea.introduction,
            'name_1': idea.name_1,
            'kudos': idea.kudos
        }
        for idea in ideas
    ]

    return render_template('idea_overview.html', ideas=ideas_info)


@app.route('/increase_kudos/<idea_id>')
def increase_kudos(idea_id):
    idea_id = int(idea_id)
    idea = dataset.get_idea_by_id(idea_id)
    if idea:
        idea.increase_kudos()
        dataset.save_to_excel()
        return str(idea.kudos)
    return "Idea not found", 404


@app.route('/increase_comment_kudos/<comment_id>')
def increase_comment_kudos(comment_id):
    comment_id = int(comment_id)
    comment = dataset.get_comment_by_id(comment_id)
    if comment:
        comment.increase_kudos()
        dataset.save_to_excel()
        return str(comment.kudos)
    return "Comment not found", 404


@app.route('/idea/<idea_id>')
def idea(idea_id):
    """
    Renders the idea overview
    """
    idea_id = int(idea_id)
    idea = dataset.get_idea_by_id(idea_id)
    if idea:
        return render_template('idea_detail.html', idea=idea)
    else:
        return "Idea not found", 404


@app.route('/add_idea', methods=['GET', 'POST'])
def add_idea():
    if request.method == 'POST':
        name = request.form['name']
        introduction = request.form['introduction']
        business_case = request.form['business_case']
        name_1 = request.form['name_1']
        department = request.form['department']

        dataset.add_idea(name, introduction, business_case, name_1, department)
        dataset.save_to_excel()
        return redirect(url_for('index'))
    return render_template('add_idea.html')


@app.route('/add_comment/<idea_id>', methods=['GET', 'POST'])
def add_comment(idea_id):
    idea_id = int(idea_id)
    if request.method == 'POST':
        text = request.form['text']

        dataset.add_comment(idea_id, text)
        dataset.save_to_excel()
        return redirect(url_for('idea', idea_id=idea_id))
    return render_template('add_comment.html', idea_id=idea_id)

if __name__ == '__main__':
    app.run(debug=True)
