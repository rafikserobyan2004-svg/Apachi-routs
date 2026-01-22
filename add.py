# ==========================================
# ԲԼՈԿ 1: Գրադարաններ, Կարգավորումներ և Օգնող ֆունկցիաներ
# ==========================================
import json, os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "points.txt")
TYPES_FILE = os.path.join(BASE_DIR, "types.txt")
ROUTES_FILE = os.path.join(BASE_DIR, "routes.txt")

def get_json_data(filename):
    if not os.path.exists(filename): return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return []

def save_json_data(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except: pass

def get_point_types():
    if not os.path.exists(TYPES_FILE): return ["VIP", "VIP-2"] 
    try:
        with open(TYPES_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except: return []

# ==========================================
# ԲԼՈԿ 2: Վալիդացիա (Validations)
# ==========================================
def parse_point_form(form):
    name = form.get("name", "").strip()
    p_type = form.get("type", "").strip()
    if not name or len(name) > 100: return None, "Անվանումը պարտադիր է"
    if not p_type: return None, "Տեսակը պարտադիր է"
    try:
        lat, lon = float(form["lat"]), float(form["lon"])
    except: return None, "Կոորդինատները սխալ են"
    
    bg = form.get("bg", "#2563eb").lower()
    fg = form.get("fg", "#ffffff").lower()
    return {"name": name, "lat": lat, "lon": lon, "bg": bg, "fg": fg, "type": p_type}, None

def parse_route_form(form):
    name = form.get("name", "").strip()
    if not name: return None, "Երթուղու անունը պարտադիր է"
    indices_str = form.get("indices", "")
    try:
        indices = [int(x) for x in indices_str.split(",") if x.strip()]
    except: indices = []
    
    color = form.get("color", "#ff0000")
    return {"name": name, "points": indices, "color": color}, None

# ==========================================
# ԲԼՈԿ 3: Flask Routes և API
# ==========================================
@app.route("/")
def index():
    return render_template("index.html", 
                           points=get_json_data(DATA_FILE), 
                           routes=get_json_data(ROUTES_FILE),
                           point_types=get_point_types())

# --- API ---
@app.route("/save_point", methods=["POST"])
def save_point():
    points = get_json_data(DATA_FILE)
    idx = request.form.get("index")
    data, error = parse_point_form(request.form)
    if error: return jsonify({"status": "err", "msg": error})

    if idx: 
        try: points[int(idx)] = data
        except: return jsonify({"status": "err", "msg": "Սխալ"})
    else: points.append(data)
    
    save_json_data(DATA_FILE, points)
    return jsonify({"status": "ok", "point": data, "index": idx})

@app.route("/delete_point", methods=["POST"])
def delete_point():
    points = get_json_data(DATA_FILE)
    try:
        idx = int(request.form["index"])
        points.pop(idx)
        save_json_data(DATA_FILE, points)
        return jsonify({"status": "ok"})
    except: return jsonify({"status": "err", "msg": "Սխալ"})

@app.route("/save_route", methods=["POST"])
def save_route():
    routes = get_json_data(ROUTES_FILE)
    idx = request.form.get("index")
    data, error = parse_route_form(request.form)
    if error: return jsonify({"status": "err", "msg": error})

    if idx:
        try: routes[int(idx)] = data
        except: return jsonify({"status": "err", "msg": "Սխալ"})
    else: routes.append(data)

    save_json_data(ROUTES_FILE, routes)
    return jsonify({"status": "ok", "route": data, "index": idx})

@app.route("/delete_route", methods=["POST"])
def delete_route():
    routes = get_json_data(ROUTES_FILE)
    try:
        idx = int(request.form["index"])
        routes.pop(idx)
        save_json_data(ROUTES_FILE, routes)
        return jsonify({"status": "ok"})
    except: return jsonify({"status": "err", "msg": "Սխալ"})

if __name__ == "__main__":
    app.run(debug=True)