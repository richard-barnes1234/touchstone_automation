# server.py — Flask backend for Touchstone Results Dashboard
# Run: python server.py
# Deploy: Azure App Service (Python 3.12)

from flask import Flask, jsonify, request, send_file, render_template_string
import urllib3
import pandas as pd
from io import BytesIO
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__, static_folder='static', template_folder='templates')

# ── Cache ─────────────────────────────────────────────────────────────────────
_cache = {}


# ── Excel builder ─────────────────────────────────────────────────────────────
def format_sheet(ws):
    thin = Border(
        left=Side(style="thin", color="D1D5DB"),
        right=Side(style="thin", color="D1D5DB"),
        top=Side(style="thin", color="D1D5DB"),
        bottom=Side(style="thin", color="D1D5DB"),
    )
    for cell in ws[1]:
        cell.font = Font(name="Calibri", bold=True, color="FFFFFF", size=10)
        cell.fill = PatternFill("solid", fgColor="1E3A5F")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin
    ws.row_dimensions[1].height = 28
    for row_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
        bg = "F0F4F8" if row_idx % 2 == 0 else "FFFFFF"
        for cell in row:
            cell.font = Font(name="Calibri", size=9)
            cell.fill = PatternFill("solid", fgColor=bg)
            cell.alignment = Alignment(horizontal="left", vertical="center")
            cell.border = thin
    for col_idx, col_cells in enumerate(ws.columns, start=1):
        max_len = max((len(str(c.value)) for c in col_cells if c.value), default=10)
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 4, 45)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions


def build_excel(meta, datasets):
    wb = Workbook()
    # Remove default sheet — we only want data sheets, no summary
    wb.remove(wb.active)

    for sheet_name, df in datasets.items():
        if df is not None and not df.empty:
            ws_data = wb.create_sheet(title=sheet_name[:31])
            for col_idx, col_name in enumerate(df.columns, start=1):
                ws_data.cell(row=1, column=col_idx, value=col_name)
            for row_idx, row_data in enumerate(df.itertuples(index=False), start=2):
                for col_idx, value in enumerate(row_data, start=1):
                    ws_data.cell(row=row_idx, column=col_idx, value=value)
            format_sheet(ws_data)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# ── API Routes ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.route("/api/projects")
def api_projects():
    try:
        if "projects" not in _cache:
            from get_analysis_sids import get_all_projects
            _cache["projects"] = get_all_projects()
        return jsonify({"ok": True, "data": _cache["projects"], "count": len(_cache["projects"])})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/analyses/loss/<project_sid>")
def api_loss_analyses(project_sid):
    try:
        from get_analysis_sids import get_analyses_for_project
        project_name = request.args.get("project_name", "")
        data = get_analyses_for_project(project_sid, project_name)
        return jsonify({"ok": True, "data": data, "count": len(data)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/analyses/haz/<project_sid>")
def api_haz_analyses(project_sid):
    try:
        from get_analysis_sids import get_hazard_analyses_for_project
        project_name = request.args.get("project_name", "")
        data = get_hazard_analyses_for_project(project_sid, project_name)
        return jsonify({"ok": True, "data": data, "count": len(data)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/results/loss/<analysis_sid>")
def api_loss_results(analysis_sid):
    try:
        from touchstone_client import get_all_loss_data
        results = get_all_loss_data(int(analysis_sid))
        data = {}
        for k, df in results.items():
            if not df.empty:
                data[k] = {
                    "columns": list(df.columns),
                    "rows":    df.values.tolist(),
                    "count":   len(df)
                }
        return jsonify({"ok": True, "data": data})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/results/haz/<analysis_sid>")
def api_haz_results(analysis_sid):
    try:
        from touchstone_client import get_hazard_results
        results = get_hazard_results(int(analysis_sid))
        data = {}
        for k, df in results.items():
            if not df.empty:
                df = df.replace([float('inf'), float('-inf')], None)
                df = df.where(pd.notnull(df), None)
                rows = []
                for row in df.values.tolist():
                    clean = [None if (v != v or v is None) else v for v in row]
                    rows.append(clean)
                data[k] = {
                    "columns": list(df.columns),
                    "rows":    rows,
                    "count":   len(df)
                }
        return jsonify({"ok": True, "data": data})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/download", methods=["POST"])
def api_download():
    try:
        body          = request.json
        meta          = body.get("meta", {})
        raw_datasets  = body.get("datasets", {})
        analysis_type = meta.get("analysis_type", "LOSS")

        datasets = {}
        for name, payload in raw_datasets.items():
            if payload and payload.get("columns"):
                df = pd.DataFrame(payload["rows"], columns=payload["columns"])
                datasets[name] = df

        excel_file = build_excel(meta, datasets)

        # Use custom filename if provided, else generate one
        custom = meta.get("custom_filename", "").strip()
        if custom:
            filename = custom if custom.endswith(".xlsx") else custom + ".xlsx"
        else:
            safe = "".join(c for c in meta.get("analysis_name","report") if c.isalnum() or c in " _-")[:40].strip()
            filename = f"Touchstone_{analysis_type}_{safe}_{meta.get('analysis_sid','')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            excel_file,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)