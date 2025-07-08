import os
from flask import jsonify
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .github_api import (
    get_workflows,
    trigger_workflow,
    get_workflow_runs,
    get_user_repositories
)
from .db import log_build_to_db

bp = Blueprint('routes', __name__)

@bp.route('/', methods=['GET', 'POST'])
def home():
    print("\n[DEBUG] home() route hit")

    # Get all user repos for dropdown
    repositories = get_user_repositories()

    # Determine selected repo
    selected_repo = request.form.get("repo") if request.method == "POST" else os.getenv("REPO_NAME")
    owner = os.getenv("REPO_OWNER")

    print(f"[DEBUG] Selected repo: {selected_repo}")

    # Temporarily override environment var for this request
    os.environ["REPO_NAME"] = selected_repo

    # Fetch workflows and runs for selected repo
    workflows = get_workflows()
    workflow_runs = get_workflow_runs()

    return render_template(
        "dashboard.html",
        repositories=repositories,
        selected_repo=selected_repo,
        workflows=workflows,
        workflow_runs=workflow_runs
    )

@bp.route('/trigger/<int:workflow_id>', methods=['POST'])
def trigger(workflow_id):
    print(f"\n[DEBUG] trigger() called for workflow_id={workflow_id}")

    selected_repo = request.form.get("repo") or os.getenv("REPO_NAME")
    os.environ["REPO_NAME"] = selected_repo

    success = trigger_workflow(workflow_id)

    workflows = get_workflows()
    workflow_name = next((wf['name'] for wf in workflows if wf['id'] == workflow_id), "Unknown")

    if success:
        flash("Workflow triggered successfully!", "success")
        log_build_to_db(
            workflow_name=workflow_name,
            run_id=0,
            status="triggered",
            conclusion="pending",
            triggered_by="manual"
        )
    else:
        flash("Failed to trigger workflow.", "error")

    return redirect(url_for('routes.home'))

@bp.route('/stats', methods=["GET"])
def stats():
    from .db import get_db_connection

    start = request.args.get("start")
    end = request.args.get("end")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM build_history"
    params = []

    if start and end:
        query += " WHERE DATE(timestamp) BETWEEN %s AND %s"
        params.extend([start, end])

    cursor.execute(query, params)
    builds = cursor.fetchall()

    total = len(builds)
    success = sum(1 for b in builds if b['conclusion'] == 'success')
    failed = sum(1 for b in builds if b['conclusion'] == 'failure')
    triggered = sum(1 for b in builds if b['triggered_by'] == 'manual')

    cursor.close()
    conn.close()

    return render_template("statistics.html", builds=builds, total=total, success=success, failed=failed, triggered=triggered)

@bp.route('/api/log-build', methods=['POST'])
def api_log_build():
    data = request.json
    required_keys = ["workflow_name", "run_id", "status", "conclusion", "triggered_by"]

    if not all(k in data for k in required_keys):
        return jsonify({"error": "Missing data in request"}), 400

    try:
        log_build_to_db(
            workflow_name=data["workflow_name"],
            run_id=data["run_id"],
            status=data["status"],
            conclusion=data["conclusion"],
            triggered_by=data["triggered_by"]
        )
        return jsonify({"message": "Build logged successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500