from flask import Blueprint, jsonify

from ..database.bootstrap_members_from_excel import seed_members_from_excel

DevSeedBlueprint = Blueprint("dev_seed", __name__, url_prefix="/dev")


@DevSeedBlueprint.route("/seed-members", methods=["GET", "POST"])
def seed_members_route():
    """
    One-time / repeatable: load member-app.xlsx into ``membership`` (dashboard source).
    Requires admin or officer session (see globalAuth RBAC for /api/dev).
    """
    payload = seed_members_from_excel()
    status = 200 if payload.get("success") else 400
    return jsonify(payload), status
