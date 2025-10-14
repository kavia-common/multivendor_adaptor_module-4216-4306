from flask import jsonify

def error_response(code: str, message: str, details=None, status=400):
    return jsonify({"code": code, "message": message, "details": details or {}}), status

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return error_response("bad_request", "Bad request", {"error": str(e)}, 400)

    @app.errorhandler(404)
    def not_found(e):
        return error_response("not_found", "Not found", {"error": str(e)}, 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response("method_not_allowed", "Method not allowed", {"error": str(e)}, 405)

    @app.errorhandler(500)
    def server_error(e):
        return error_response("server_error", "Internal server error", {"error": str(e)}, 500)
