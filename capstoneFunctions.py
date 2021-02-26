from app import Pharmaceutical, Structured_Product_Label, National_Drug_Code
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
import json

def add_to_db(db, input_string):
    from app import Pharmaceutical, Structured_Product_Label, National_Drug_Code
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

# Needs to be rewritten
def output_data(db, input_string):
    # Check Local DB
    r_set = con.execute('''
                        SELECT Name
                        FROM Pharmaceutical
                        ''')
    names = [i[0] for i in r_set.fetchall()]
    if input_string in names:
        question_marks = ','.join(len(pharm_id(con, input_string))*'?')
        r_set = con.execute(f'''
                            SELECT
                                p.Name,
                                s.SETID,
                                s.Version,
                                s.publication_date,
                                s.Title,
                                group_concat(n.NDC)
                            FROM Pharmaceutical AS p
                            JOIN Structured_Product_Label AS s
                            ON s.Pharm_ID = p.Pharm_ID
                            JOIN National_Drug_Code AS n
                            ON n.SPL_ID = s.SPL_ID
                            WHERE p.Pharm_ID
                            IN ({question_marks})
                            GROUP BY s.SPL_ID
                            ORDER BY s.SPL_ID
                            ''', pharm_id(con, input_string))
        data = r_set.fetchall()
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
            ndcs = get_ndcs(con, record["setid"])
            row = (drug_name,
                   record["setid"],
                   record['spl_version'],
                   record['published_date'],
                   title,
                   ndcs)
            data.append(row)
    column_names = ["Drug Name", "Set ID", "SPL_Ver", "Pub Date", "Title", "NDC #s"]
    return column_names, data
