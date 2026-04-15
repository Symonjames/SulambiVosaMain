from flask import Blueprint
from .routes.auth import AuthBlueprint
from .routes.events import EventsBlueprint
from .routes.membership import MembershipBlueprint
from .routes.evaluation import EvaluationBlueprint
from .routes.requirements import RequirementsBlueprint
from .routes.accounts import AccountsBlueprint
from .routes.dashboard import DashboardBlueprint
from .routes.reports import ReportsBlueprint
from .routes.feedback import FeedbackBlueprint
from .routes.analytics import AnalyticsBlueprint
from .routes.dev_seed import DevSeedBlueprint
from .middlewares.globalAuth import global_api_auth

ApiBlueprint = Blueprint('api', __name__, url_prefix='/api')

# Global auth + RBAC for all /api/* routes (runs before any blueprint handler)
ApiBlueprint.before_request(global_api_auth)

@ApiBlueprint.get('/')
def apiIndex():
  return {
    "message": "Api route is working"
  }

ApiBlueprint.register_blueprint(AuthBlueprint)
ApiBlueprint.register_blueprint(EventsBlueprint)
ApiBlueprint.register_blueprint(MembershipBlueprint)
ApiBlueprint.register_blueprint(EvaluationBlueprint)
ApiBlueprint.register_blueprint(RequirementsBlueprint)
ApiBlueprint.register_blueprint(AccountsBlueprint)
ApiBlueprint.register_blueprint(DashboardBlueprint)
ApiBlueprint.register_blueprint(ReportsBlueprint)
ApiBlueprint.register_blueprint(FeedbackBlueprint)
ApiBlueprint.register_blueprint(AnalyticsBlueprint)
ApiBlueprint.register_blueprint(DevSeedBlueprint)