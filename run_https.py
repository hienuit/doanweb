import ssl
from app import create_app

app = create_app()

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('localhost+2.pem', 'localhost+2-key.pem')
    app.run(host='127.0.0.1', port=5000, ssl_context=context, debug=True)
