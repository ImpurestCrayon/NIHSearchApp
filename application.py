from applicationFunctions import add_to_db, output_data
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy

application = app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Pharmaceutical(db.Model):
    __tablename__ = 'Pharmaceutical'
    Pharm_ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.Text, nullable=False) #unique=True

    def __repr__(self):
            return "<Pharmaceutical(Pharm ID='%s')>" % (self.Pharm_ID)
class Structured_Product_Label(db.Model):
    __tablename__ = 'Structured_Product_Label'
    SPL_ID = db.Column(db.Integer, primary_key=True)
    SetID = db.Column(db.Text, nullable=False) #unique=True
    Pharm_ID = db.Column(db.Integer,
     db.ForeignKey('Pharmaceutical.Pharm_ID'),
     nullable=False)
    Version = db.Column(db.Integer, nullable=False)
    Title = db.Column(db.Text, nullable=False)
    publication_date = db.Column(db.Text, nullable=False)

    def __repr__(self):
            return "<Structured_Product_Label(SPL ID='%s')>" % (self.SPL_ID)
class National_Drug_Code(db.Model):
    __tablename__ = 'National_Drug_Code'
    NDC_ID = db.Column(db.Integer, primary_key=True)
    SPL_ID =  db.Column(db.Integer,
     db.ForeignKey('Structured_Product_Label.SPL_ID'),
     nullable=False)
    NDC = db.Column(db.Text, nullable=False) #unique=True

    def __repr__(self):
            return "<Pharmaceutical(NDC ID='%s')>" % (self.NDC_ID)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/verify', methods=['POST', 'GET'])
def verify():
    if request.method == 'POST':
        content = request.form['content']
        try:
            if request.form.get('add-to-db'):
                add_to_db(content)
            return redirect(f'/output/{content}')
        except:
            return 'There was an issue adding this to the DB'
    else:
        return redirect('/')

@app.route('/output/<content>')
def output(content):
    data = output_data(content)
    return render_template('output.html', data=data)


if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)
