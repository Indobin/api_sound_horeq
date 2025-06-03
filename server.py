from app.main import app
from mangum import Mangum

if not callable(app):
    print(f"❌ ERROR: `app` is not a callable object: {type(app)}")
else:
    print(f"✅ app is of type: {type(app)}")

handler = Mangum(app)
