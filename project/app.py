import os
import re, json
import requests
import markdown2
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, Response, stream_with_context
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from helpers import apology, login_required
from datetime import datetime

load_dotenv()
api_key = os.getenv("PERPLEXITY_API_KEY")

# Configure application
app = Flask(__name__)

@app.template_filter('markdown')
def markdown_filter(text):
    return markdown2.markdown(text)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///stats.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# HOMEPAGE
@app.route("/")
@login_required
def index():
    return render_template("index.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")

# LOGOUT
@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username")
        if not password:
            return apology("must provide password")
        if not confirmation:
            return apology("must confirm password")
        if password != confirmation:
            return apology("passwords must match")

        try:
            hash = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
            return redirect("/login")
        except ValueError:
            return apology("username already exists")
    else:
        return render_template("register.html")

# CHANGE PASSWORD
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        if not old_password or not new_password or not confirmation:
            return apology("All fields required")

        if new_password != confirmation:
            return apology("New passwords don't match")

        user_hash = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])[0]["hash"]

        if not check_password_hash(user_hash, old_password):
            return apology("Current password is incorrect")

        new_hash = generate_password_hash(new_password)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash, session["user_id"])
        flash("Password changed!")
        return redirect("/")
    else:
        return render_template("change_password.html")

@app.route("/query", methods=["POST"])
@login_required
def query():

    query_text = request.form.get("query")
    start_year = request.form.get("startYear")
    end_year = request.form.get("endYear")
    geo_area = request.form.get("geoArea", "italy")

    if not query_text:
        return apology("Devi inserire una domanda")

    area_config = {
        "italy": {"name": "Italia"},
        "eu": {"name": "Europa"},
        "world": {"name": "Mondo"},
        "regions": {"name": "Regioni italiane"}
    }

    selected_area = area_config[geo_area]

    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # PROMPT
    system_prompt = (
        f"You are an expert statistical analyst specializing in socio-economic data analysis for {selected_area['name']}. "
        "IMPORTANT: Detect the language of the user's input and respond EXCLUSIVELY in that language for ALL parts of the response. "
        "Follow these instructions CAREFULLY:\n\n"

        "OUTPUT FORMAT:\n"
        "1. Start IMMEDIATELY with the raw JSON, without any headers or introductory text\n"
        "2. The JSON must start directly with '{'\n"
        "3. NEVER include phrases like 'Here's the JSON', 'JSON for Charts', or similar\n"
        "4. After the JSON, proceed directly with the analysis in the user's language\n"
        "5. Don't use headers like 'Analysis', 'Markdown Analysis' or similar\n\n"

        "Follow these instructions CAREFULLY:\n\n"

        "1. DATA SELECTION AND VALIDATION:\n"
        f"- Use ONLY official sources for {selected_area['name']}\n"
        "- Give absolute priority to national sources of the geographic area\n"
        "- Use international sources ONLY if national ones are unavailable\n"
        "- If the specific requested data is not available:\n"
        "  a) Look for data from the broader category\n"
        "  b) Search for correlated data\n"
        "  c) Use proxy data from reliable sources\n"
        "- In absence of direct data, combine different sources for a reasonable estimate\n"
        "- ALWAYS specify when using approximations or estimates\n\n"

        "2. TIME RANGE MANAGEMENT:\n"
        f"- Requested period: from {start_year} to {end_year}\n"
        "- If data doesn't cover the entire period:\n"
        "  a) Use the longest available period\n"
        "  b) Consider trends of related categories\n"
        "  c) Integrate with estimates based on available data\n\n"

        "3. CHART STRUCTURE AND OBJECTIVE:\n"
        "- You must produce 4 charts in total, all in a single JSON\n"
        "- Chart 1 (main): answers the user's main question\n"
        "- Chart 2 (composition): shows internal distribution/composition of the main data\n"
        "- Charts 3 and 4 (related): show the trend of two correlated socio-economic or demographic variables\n"
        "- Use complete annual time series\n"
        "- If using approximated or correlated data, specify in the title\n"
        "- For estimates, provide confidence ranges when possible\n\n"

        "4. CRITICAL - JSON FORMAT:\n"
        "The JSON must be clean and without comments or notes. Example of final structure:\n"
        "```json\n"
        "{\n"
        '  "charts": [\n'
        '    {\n'
        '      "type": "line",\n'
        '      "labels": ["2020", "2021", "2022"],\n'
        '      "data": [125, 130, 132],\n'
        '      "title": "Average annual salary in Italy",\n'
        '      "timeRange": {"start": "2020", "end": "2022"},\n'
        '      "unit": "EUR",\n'
        '      "format": "decimal",\n'
        '      "source": "ISTAT",\n'
        '      "data_frequency": "annual",\n'
        '      "geo_area": "Italy",\n'
        '      "range": {"min": 125, "max": 132}\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "```\n\n"

        "5. ANALYSIS STRUCTURE:\n"
        "After the JSON, develop a thorough analysis that includes:\n"
        "- Source and Methodology:\n"
        "  * Describe all sources used in detail\n"
        "  * Explain data collection and processing\n"
        "  * Illustrate any estimation or approximation methods\n"
        "  * Discuss source quality and reliability\n\n"
        "- Trend Analysis:\n"
        "  * Describe the historical trend in detail\n"
        "  * Analyze significant variations and their causes\n"
        "  * Examine correlations between variables\n"
        "  * Identify cyclical or seasonal patterns\n"
        "  * Compare data with relevant benchmarks\n\n"
        "- Technical Details:\n"
        "  * Discuss any data anomalies\n"
        "  * Explain methodological choices\n"
        "  * Analyze survey limitations\n"
        "  * Indicate estimate error margins\n\n"
        "- Impact and Implications:\n"
        "  * Analyze economic and social consequences\n"
        "  * Evaluate effects on other related indicators\n"
        "  * Discuss possible future developments\n"
        "  * Compare with international trends\n\n"
        "- Additional Considerations:\n"
        "  * Propose alternative data interpretations\n"
        "  * Suggest additional indicators to monitor\n"
        "  * Discuss potential future developments\n"
        "  * Analyze impact of specific policies or events\n\n"

        "6. DATA QUALITY:\n"
        "- Always prioritize raw data over processed data\n"
        "- Specify confidence level of estimates\n"
        "- Indicate any discontinuities in time series\n"
        "- Report possible discrepancies between sources\n"
        "- For missing data, specify interpolation method\n\n"

        "7. CHART CONSISTENCY:\n"
        "- Maintain scale consistency between related charts\n"
        "- Use same units of measurement where possible\n"
        "- Align time intervals between charts\n"
        "- Use consistent colors for same elements\n"
        "- Maintain same aggregation level\n\n"

        "CHART COMBINATION EXAMPLES:\n"
        "Example 1 (average meat consumption):\n"
        "- Chart 1 (line): Average meat consumption trend\n"
        "- Chart 2 (pie): Consumption composition by type\n"
        "- Chart 3 (bar): Food inflation\n"
        "- Chart 4 (bar): Feed imports\n\n"

        "Example 2 (wine production):\n"
        "- Chart 1 (line): Total wine production\n"
        "- Chart 2 (pie): Composition by grape variety\n"
        "- Chart 3 (bar): Grape price trend\n"
        "- Chart 4 (bar): Wine export\n\n"

        "Example 3 (birth rate):\n"
        "- Chart 1 (line): Birth rate\n"
        "- Chart 2 (pie): Regional composition\n"
        "- Chart 3 (bar): Female employment\n"
        "- Chart 4 (bar): Aging index\n\n"

        "REMEMBER: Detect and use EXCLUSIVELY the language of the user's input in EVERY part of the response.\n"
    )

    data = {
        "model": "llama-3.1-sonar-large-128k-online",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query_text}
        ],
        "temperature": 0.1
    }

    string_pattern = r'(?<!\\)"([^"\\]*(?:\\.[^"\\]*)*)"'

    def escape_internal_quotes(json_str):
        matches = re.finditer(string_pattern, json_str)
        last_pos = 0
        new_json = ""
        for match in matches:
            start, end = match.span()
            new_json += json_str[last_pos:start]
            content = match.group(1)
            content_fixed = re.sub(r'(?<!\\)"', r'\"', content)
            new_json += f"\"{content_fixed}\""
            last_pos = end
        new_json += json_str[last_pos:]
        return new_json

    def generate():
        try:
            # API call
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            api_response = response.json()
            citations = api_response.get('citations', [])

            full_text = api_response['choices'][0]['message']['content']

            json_pattern = r'```json\s*({[^`]*})\s*```'
            json_match = re.search(json_pattern, full_text, re.DOTALL)

            if json_match:
                json_str = json_match.group(1).strip()
                try:
                    cleaned_json = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)
                    cleaned_json = '\n'.join(line for line in cleaned_json.split('\n') if line.strip())
                    cleaned_json = (cleaned_json
                                    .replace('None', 'null')
                                    .replace('True', 'true')
                                    .replace('False', 'false'))
                    cleaned_json = escape_internal_quotes(cleaned_json)

                    print("JSON originale:", json_str)
                    print("JSON pulito:", cleaned_json)

                    graph_data = json.loads(cleaned_json)
                    text_parts = full_text.split('```')
                    explanation = ''.join([part for part in text_parts if '{' not in part]).strip()
                except json.JSONDecodeError as e:
                    error_location = e.pos
                    context = cleaned_json[max(0, error_location-50):min(len(cleaned_json), error_location+50)]
                    yield "data: " + json.dumps({"type": "error", "content": f"Errore JSON alla posizione {error_location}. Contesto: ...{context}..."}) + "\n\n"
                    return
            else:
                graph_data = {}
                explanation = full_text

            query_metadata = {
                "start_year": start_year,
                "end_year": end_year,
                "geo_area": geo_area,
                "citations": citations
            }

            db.execute("""
                INSERT INTO queries
                (user_id, query_text, response_text, graph_data, metadata)
                VALUES (?, ?, ?, ?, ?)
            """,
            session["user_id"],
            query_text,
            explanation,
            json.dumps(graph_data),
            json.dumps(query_metadata))

            query_id = db.execute("SELECT id FROM queries WHERE user_id = ? ORDER BY id DESC LIMIT 1", session["user_id"])[0]['id']

            yield "data: " + json.dumps({"type": "redirect", "url": f"/results/{query_id}"}) + "\n\n"

        except requests.RequestException as e:
            yield "data: " + json.dumps({"type": "error", "content": f"Errore nella chiamata API: {str(e)}"}) + "\n\n"
        except Exception as e:
            yield "data: " + json.dumps({"type": "error", "content": f"Si è verificato un errore: {str(e)}"}) + "\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route("/results/<int:query_id>")
@login_required
def results(query_id):
    query = db.execute("""
        SELECT query_text, response_text, graph_data, metadata
        FROM queries
        WHERE id = ? AND user_id = ?
    """, query_id, session["user_id"])

    if not query:
        return apology("Query non trovata")

    graph_data = json.loads(query[0]["graph_data"]) if query[0]["graph_data"] else {}
    charts = graph_data.get("charts", [])
    metadata = json.loads(query[0]["metadata"]) if query[0]["metadata"] else {}
    citations = metadata.get("citations", [])

    response_text = query[0]["response_text"]

    return render_template("results.html",
                         query_text=query[0]["query_text"],
                         response_text=response_text,
                         charts=json.dumps(charts),
                         citations=citations)

@app.route("/history")
@login_required
def history():
    queries = db.execute("""
        SELECT id, query_text, response_text, graph_data, timestamp
        FROM queries
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, session["user_id"])

    for query in queries:
        query["timestamp"] = datetime.strptime(query["timestamp"], "%Y-%m-%d %H:%M:%S")

    return render_template("history.html", queries=queries)
