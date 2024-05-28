from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from dataset_parsing import Dataset
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'o;rughzdfngkjeirurgh'

dataset = Dataset('dataset.xlsx')

# Define the forms
class ProposalForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    title = StringField('Proposal Title', validators=[DataRequired()])
    text = TextAreaField('Proposal Text', validators=[DataRequired()])
    submit = SubmitField('Next')

class DetailsForm(FlaskForm):
    activities = TextAreaField('Activities of the Project')
    resources = TextAreaField('Required Resources')
    value_propositions = TextAreaField('Value Propositions')
    next = SubmitField('Next')

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
            'kudos': idea.kudos,
            'status': idea.status,
            'date': idea.datetime.strftime('%d/%m/%Y %H:%M')
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

@app.route('/idea/<int:idea_id>', methods=['GET', 'POST'])
def idea(idea_id):
    idea = dataset.get_idea_by_id(idea_id)
    if not idea:
        return "Idea not found", 404

    if request.method == 'POST':
        text = request.form['text']
        dataset.add_comment(idea_id, text)
        dataset.save_to_excel()
        return redirect(url_for('idea', idea_id=idea_id))

    comments_info = [
        {
            'comment_id': comment.comment_id,
            'text': comment.text,
            'kudos': comment.kudos,
            'datetime': comment.datetime.strftime('%d/%m/%Y %H:%M')
        }
        for comment in idea.comments
    ]

    return render_template('idea_detail.html', idea=idea, comments=comments_info)

@app.route('/add_idea', methods=['GET', 'POST'])
def add_idea():
    if request.method == 'POST':
        name = request.form['name']
        introduction = request.form['introduction']
        name_1 = request.form['name_1']

        idea_id = dataset.add_idea(name, introduction, name_1)
        dataset.save_to_excel()

        return redirect(url_for('idea', idea_id=idea_id))
    return render_template('idea_detail.html')

@app.route('/proposal', methods=['GET', 'POST'])
def form():
    form = ProposalForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['title'] = form.title.data
        session['text'] = form.text.data
        return redirect(url_for('details'))
    return render_template('form.html', form=form)

@app.route('/details', methods=['GET', 'POST'])
def details():
    form = DetailsForm()
    if form.validate_on_submit():
        session['activities'] = form.activities.data
        session['resources'] = form.resources.data
        session['value_propositions'] = form.value_propositions.data
        return redirect(url_for('review'))
    return render_template('details.html', form=form)

@app.route('/review', methods=['GET', 'POST'])
def review():
    if request.method == 'POST':
        if 'submit' in request.form:
            flash('Form submitted successfully!')
            session.clear()
            return redirect(url_for('success'))
        elif 'cancel' in request.form:
            session.clear()
            return redirect(url_for('form'))
    similar_proposals = ["Similar Proposal 1", "Similar Proposal 2", "Similar Proposal 3"]
    return render_template('review.html', similar_proposals=similar_proposals)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/admin_view/<int:idea_id>', methods=['GET', 'POST'])
def admin_view(idea_id):
    idea = dataset.get_idea_by_id(idea_id)
    if not idea:
        return "Idea not found", 404

    if request.method == 'POST':
        idea.name = request.form.get('name')
        idea.name_1 = request.form.get('name_1')
        idea.introduction = request.form.get('introduction')
        idea.key_partners = request.form.get('key_partners')
        idea.status = request.form.get('status')
        idea.type_activity = request.form.get('type_activity')
        idea.risk = request.form.get('risk')
        idea.priority = request.form.get('priority')
        idea.benefits = request.form.get('benefits')
        idea.digital_trend = request.form.get('digital_trend')
        idea.expected_maturity = request.form.get('expected_maturity')
        idea.expected_fte = request.form.get('expected_fte')

        dataset.save_to_excel()  # Save changes to the backend
        flash('Proposal updated successfully!')
        return redirect(url_for('admin_view', idea_id=idea_id))

    return render_template('admin_view.html', idea=idea)



if __name__ == '__main__':
    app.run(debug=True)
