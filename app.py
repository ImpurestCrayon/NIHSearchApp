from capstonefunctions import add_to_db, output_data
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Pharmaceutical(db.Model):
    __tablename__ = 'Pharmaceutical'
    Pharm_ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.Text, unique=True, nullable=False)

    def __repr__(self):
            return "<Pharmaceutical(Name='%s')" % (self.Name)

class Structured_Product_Label(db.Model):
    __tablename__ = 'Structured_Product_Label'
    SPL_ID = db.Column(db.Integer, primary_key=True)
    SetID = db.Column(db.Text, unique=True, nullable=False)
    Pharm_ID = db.Column(db.Integer,
     db.ForeignKey('Pharmaceutical.Pharm_ID'),
     nullable=False)
    Version = db.Column(db.Integer, nullable=False)
    Title = db.Column(db.Text, nullable=False)
    publication_date = db.Column(db.Text, nullable=False)

    def __repr__(self):
            return "<Structured_Product_Label(SetID='%s', Pharm_ID='%s', \
                Version='%s', Title='%s', publication_date='%s')" % (
                self.SetID, self.Pharm_ID, self.Version, self.Title,
                self.Version, self.Title, self.publication_date)

class National_Drug_Code(db.Model):
    __tablename__ = 'National_Drug_Code'
    NDC_ID = db.Column(db.Integer, primary_key=True)
    SPL_ID =  db.Column(db.Integer,
     db.ForeignKey('Structured_Product_Label.SPL_ID'),
     nullable=False)
    NDC = db.Column(db.Text, unique=True, nullable=False)

    def __repr__(self):
            return "<Pharmaceutical(SPL_ID='%s', NDC='%s')" %
            (self.SPL_ID, self.NDC)

'''@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)'''


@app.route('/', methods=['POST', 'GET'])
def index_html():
    if request.method == 'POST':
        input_string = request.form['content']
        #add_to_db(db, input_string)
        data = output_data(db, input_string)
        try:
            return redirect('/')
        except:
            pass
        return input_string
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
