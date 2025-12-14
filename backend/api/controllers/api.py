from flask import Blueprint
from api.controllers.user_controller import user_bp
from api.controllers.post_controller import post_bp
from api.controllers.comment_controller import comment_bp
from api.controllers.community_controller import community_bp
from api.controllers.follow_controller import follow_bp
from api.controllers.message_controller import message_bp
from api.controllers.upload_controller import upload_bp

api_bp = Blueprint('api', __name__)

# Register all controller blueprints
api_bp.register_blueprint(user_bp)
api_bp.register_blueprint(post_bp)
api_bp.register_blueprint(comment_bp)
api_bp.register_blueprint(community_bp)
api_bp.register_blueprint(follow_bp)
api_bp.register_blueprint(message_bp)
api_bp.register_blueprint(upload_bp)