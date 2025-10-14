from app import create_app

# PUBLIC_INTERFACE
def app():
    """WSGI application entrypoint for Flask servers."""
    return create_app()

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000)
