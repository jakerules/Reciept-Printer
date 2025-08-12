"""
Error handlers for the application.
"""
from flask import render_template, jsonify, request

def register_error_handlers(app):
    """
    Register error handlers for the application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors."""
        if request.path.startswith('/api/'):
            return jsonify(error="Resource not found"), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        """Handle 500 errors."""
        if request.path.startswith('/api/'):
            return jsonify(error="Internal server error"), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(e):
        """Handle 403 errors."""
        if request.path.startswith('/api/'):
            return jsonify(error="Forbidden"), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(400)
    def bad_request(e):
        """Handle 400 errors."""
        if request.path.startswith('/api/'):
            return jsonify(error="Bad request"), 400
        return render_template('errors/400.html'), 400