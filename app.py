from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
import json

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

def add_to_db(input_string):
    if Pharmaceutical.query.filter_by(Name=input_string).first() is not None:
        print('Drug in DB.')
    else:
        # Grab Matches
        url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={input_string}"
        r = requests.get(url)
        json_dict = json.loads(r.text)
        if len(json_dict['data']) == 0:
            print(f'No Matchs Found on {url}.')
        else:
            # Set Variables
            pharmid = next_pharmid(Pharmaceutical)
            splid = next_splid(Structured_Product_Label)
            # Insert Pharmaceutical Data
            pharm_input = Pharmaceutical(Name=input_string)
            db.session.add(pharm_input)
            db.session.commit()
            # Insert Structured_Product_Label Data
            for row in json_dict['data']:
                # figure out if we don't want repeat entries or not for each Pharm ID/Set ID
                spl_input = Structured_Product_Label(
                    SetID=row['setid'],
                    Pharm_ID=pharmid,
                    Version=row['spl_version'],
                    Title=row['title'],
                    publication_date=row['published_date'])
                db.session.add(spl_input)
                db.session.commit()
                ndcs = get_ndcs(row['setid'])
                # Insert National_Drug_Code Data
                for ndc in ndcs:
                    ndc_input = National_Drug_Code(
                        SPL_ID=splid,
                        NDC=ndc)
                    db.session.add(ndc_input)
                    db.session.commit()
                # Add to splid for NDC table
                splid += 1

def next_pharmid(pharm_table):
    if pharm_table.query.order_by(pharm_table.Pharm_ID.desc()).first() is None:
        next_pharmid = 1
    else:
        next_pharmid = pharm_table.query.order_by(pharm_table.Pharm_ID.desc()).first().Pharm_ID+1
    return next_pharmid

def next_splid(spl_table):
    if spl_table.query.order_by(spl_table.SPL_ID.desc()).first() is None:
        next_splid = 1
    else:
        next_splid = spl_table.query.order_by(spl_table.SPL_ID.desc()).first().SPL_ID+1
    return next_splid

def get_ndcs(set_id):
    url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{set_id}/ndcs"
    r = requests.get(url)
    json_dict = json.loads(r.text)
    ndcs = [row['ndc'] for row in json_dict["data"]["ndcs"]]
    return ndcs

def output_data(input_string):
    # Check Local DB
    if Pharmaceutical.query.filter_by(Name=input_string).first() is not None:
        print('Drug in DB.')
        query = db.session.query(
                        Pharmaceutical.Name,
                        Structured_Product_Label.SetID,
                        Structured_Product_Label.Version,
                        Structured_Product_Label.publication_date,
                        Structured_Product_Label.Title,
                        Structured_Product_Label.SPL_ID
                    ).join(
                        Structured_Product_Label,
                        Pharmaceutical.Pharm_ID == Structured_Product_Label.Pharm_ID
                    ).filter(
                        Pharmaceutical.Name == input_string
                    ).all()
        data = list()
        for row in query:
            ndcs = db.session.query(
                        National_Drug_Code.NDC
                    ).filter(
                        National_Drug_Code.SPL_ID == row[-1]
                    ).all()
            row = list(row)
            row[-1] = ', '.join([ndc[0] for ndc in ndcs])
            data.append(row)
    else:
        data = list()
        # Check NDC DB
        # Set Variables
        row = list()
        # Grab Matches
        url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={input_string}"
        r = requests.get(url)
        json_dict = json.loads(r.text)
        for record in json_dict["data"]:
            title = record['title']
            if title.find('(') != -1:
                drug_name = title[:title.find('(')]
            elif title.find('[') != -1:
                drug_name = title[:title.find('[')]
            else:
                drug_name = input_string.upper()
            ndcs = ','.join(get_ndcs(record["setid"]))
            row = (drug_name,
                   record["setid"],
                   record['spl_version'],
                   record['published_date'],
                   title,
                   ndcs)
            data.append(row)
    # column_names = ["Drug Name", "Set ID", "SPL_Ver", "Pub Date", "Title", "NDC #s"]
    return data

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
    app.run(debug=True)
