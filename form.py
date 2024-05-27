from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

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

@app.route('/', methods=['GET', 'POST'])
def form():
    form = ProposalForm()
    if form.validate_on_submit():
        # Store the data from the first form in session
        session['name'] = form.name.data
        session['title'] = form.title.data
        session['text'] = form.text.data
        return redirect(url_for('details'))
    return render_template('form.html', form=form)

@app.route('/details', methods=['GET', 'POST'])
def details():
    form = DetailsForm()
    if form.validate_on_submit():
        # Store the data from the second form in session
        session['activities'] = form.activities.data
        session['resources'] = form.resources.data
        session['value_propositions'] = form.value_propositions.data
        return redirect(url_for('review'))
    return render_template('details.html', form=form)

@app.route('/review', methods=['GET', 'POST'])
def review():
    if request.method == 'POST':
        # Process the final submission
        if 'submit' in request.form:
            flash('Form submitted successfully!')
            # Clear the session after submission
            session.clear()
            return redirect(url_for('success'))
        elif 'cancel' in request.form:
            # Clear the session and redirect to the first form
            session.clear()
            return redirect(url_for('form'))
    # Placeholder similar proposals
    similar_proposals = ["Similar Proposal 1", "Similar Proposal 2", "Similar Proposal 3"]
    return render_template('review.html', similar_proposals=similar_proposals)

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)
