import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium", app_title="Grade Extractor")

with app.setup:
    import marimo as mo

    import json
    import pandas as pd


@app.cell
def _():
    semester = "Spring semester 2026"
    batchwise_links = {
        "MS21": "https://erp.iisermohali.ac.in/spGetRegisteredCoursesInLevel.action?level.id=1315930116",
        "MS22": "https://erp.iisermohali.ac.in/spGetRegisteredCoursesInLevel.action?level.id=1315930117",
        "MS23": "https://erp.iisermohali.ac.in/spGetRegisteredCoursesInLevel.action?level.id=1315930118",
        # "MS24": "https://erp.iisermohali.ac.in/spGetRegisteredCoursesInLevel.action?level.id=",
        # "MS25": "https://erp.iisermohali.ac.in/spGetRegisteredCoursesInLevel.action?level.id=",
    }
    return batchwise_links, semester


@app.cell(hide_code=True)
def _(semester):
    mo.md(f"""
    To check your grades of **{semester}**, follow the given steps:
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    1. Open https://erp.iisermohali.ac.in and login to your account.
    """)
    return


@app.cell(hide_code=True)
def _(batchwise_links):
    batch_dropdown = mo.ui.dropdown(options=batchwise_links).form()
    mo.vstack([
        mo.md("2. Choose your batch"),
        batch_dropdown,
    ])
    return (batch_dropdown,)


@app.cell(hide_code=True)
def _(batch_dropdown):
    mo.md(f"""
    3. Visit this link: {batch_dropdown.value}
    """)
    return


@app.cell(hide_code=True)
def _():
    form = mo.ui.text_area(placeholder="Paste JSON here...").form()
    mo.vstack([
        mo.md("4. Paste the JSON response you get from the above link into the text area below:"),
        form
    ])
    return (form,)


@app.cell
def _(form):
    mo.stop(form.value is None, mo.md("Submit the form to see the results!"))

    output = parse(form.value)
    if output['spi'] is not None:
        spi_display = mo.md(f"/// admonition | Based on the grades, your SPI is: **{output['spi']}**")
    else:
        spi_display = mo.md("/// admonition | SPI cannot be calculated as some courses do not have grades yet.")

    mo.vstack([
        mo.md("5. Profit!"),
        pd.DataFrame(output['data']),
        spi_display
    ])
    return


@app.function
def get_grade(grade_id):
    grade_details = {
        114065408: "A",
        114065409: "B",
        114065410: "C",
        114065411: "D",
        114065412: "F",
    }
    return grade_details.get(grade_id, None)


@app.function
def get_spi(courses):
    total_credits = 0
    total_points = 0
    for course in courses:
        if course["grade"] is None:
            return None

        total_credits += course["credit"]
        total_points += course["credit"] * {"A": 10, "B": 8, "C": 6, "D": 4, "F": 0}.get(course["grade"], 0)

    spi = total_points / total_credits
    return round(spi, 2)


@app.function
def parse(response):
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        return "Invalid JSON. Please check the input and try again."

    output = []
    for course in data:
        base = course[0]["syllabusCourse"]["courseClassType"]["course"]
        code = base["code"]
        name = base["name"]
        credit = int(course[0]["syllabusCourse"]["credit"])
        try:
            grade_id = course[0]["forcedGrade"]["id"]
        except KeyError:
            grade_id = None
        output.append(
            {
                "code": code,
                "name": name,
                "credit": credit,
                "grade": get_grade(grade_id),
            }
        )
    return {
        'data': output,
        'spi': get_spi(output),
    }


if __name__ == "__main__":
    app.run()
