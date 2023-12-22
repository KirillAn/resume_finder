from flask import Flask, render_template, request
import json
from script_for_search import find_similar_documents

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        wanna_job_input = request.form["wanna_job"]
        expa_input = request.form["expa"]
        city_input = request.form["city"]
        relocation_ready_input = True if "relocation_ready" in request.form else False

        similar_documents = find_similar_documents(
            wanna_job_input,
            expa_input,
            city=city_input,
            relocation_ready=relocation_ready_input,
        )

        return render_template(
            "index.html",
            similar_documents=similar_documents,
            wanna_job=wanna_job_input,
            expa=expa_input,
            city=city_input,
            relocation_ready=relocation_ready_input,
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

    app.run(debug=True)
