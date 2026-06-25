import os
import importlib
import unittest


class AppStartupTests(unittest.TestCase):
    def test_app_starts_and_renders_login_page(self):
        os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
        app_module = importlib.import_module("app")
        app = app_module.create_app()

        with app.test_client() as client:
            response = client.get("/login")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Sign In", response.data)


if __name__ == "__main__":
    unittest.main()
