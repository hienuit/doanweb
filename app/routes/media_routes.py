# app/routes/media_routes.py
from flask import Blueprint, send_from_directory,request,render_template
from app.models.destinations import search_describe

media_blueprint = Blueprint('media', __name__)

@media_blueprint.route('/video/<filename>')
def serve_video(filename):
    return send_from_directory("static/video", filename)

@media_blueprint.route('/images/<filename>')
def serve_images(filename):
    return send_from_directory("static/images", filename)

