from flask import Flask, render_template, request
import csv
from collections import defaultdict

app = Flask(__name__)

CSV_FILE = "corredors_ceap.csv"
CSV_CLUBS = "puntuacio_clubs.csv"


def load_data():
    rows = []
    with open(CSV_FILE, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["Puntuació"] = float(row["Puntuació"])
            rows.append(row)
    return rows


def load_club_points():
    clubs = []
    with open(CSV_CLUBS, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["puntsTotals"] = float(row["puntsTotals"])
            clubs.append(row)
    return clubs


@app.route("/")
def index():
    rows = load_data()
    club_rows = load_club_points()

    # Get filters
    carrera_filter = request.args.get("Cursa", "")
    corredor_filter = request.args.get("Corredor", "")

    # Apply filters
    filtered = []
    for r in rows:
        if carrera_filter and r["Cursa"] != carrera_filter:
            continue
        if corredor_filter and r["Corredor"] != corredor_filter:
            continue
        filtered.append(r)

    # Dropdown lists
    carreras = sorted(set(r["Cursa"] for r in rows))
    corredores = sorted(set(r["Corredor"] for r in rows))

    # Total points per race
    totals_by_race = defaultdict(float)
    for r in filtered:
        totals_by_race[r["Cursa"]] += r["Puntuació"]

    # Ranking athletes
    ranking = defaultdict(float)
    for r in rows:
        ranking[r["Corredor"]] += r["Puntuació"]
    ranking = sorted(ranking.items(), key=lambda x: x[1], reverse=True)

    # -------- CLUB TABLE --------
    clubs = sorted(set(r["club"] for r in club_rows))
    races = sorted(set(r["cursa"] for r in club_rows))

    # dict[club][race] = score
    club_scores = defaultdict(lambda: defaultdict(float))

    for r in club_rows:
        club_scores[r["club"]][r["cursa"]] += r["puntsTotals"]

    # totals per club
    club_totals = {}
    for club in clubs:
        club_totals[club] = sum(club_scores[club][race] for race in races)

    # sort clubs by total desc
    clubs_sorted = sorted(clubs, key=lambda c: club_totals[c], reverse=True)

    # totals per race
    race_totals = {}
    for race in races:
        race_totals[race] = sum(club_scores[c][race] for c in clubs)

    return render_template(
        "index.html",
        rows=filtered,
        carreras=carreras,
        corredores=corredores,
        carrera_filter=carrera_filter,
        corredor_filter=corredor_filter,
        totals_by_race=dict(totals_by_race),
        ranking=ranking,
        clubs_sorted=clubs_sorted,
        races=races,
        club_scores=club_scores,
        club_totals=club_totals,
        race_totals=race_totals
    )


if __name__ == "__main__":
    app.run(debug=True)
