from redash.query_runner import BaseQueryRunner, register
from redash.utils import json_dumps
import json
import requests

class CustomJsonAPI(BaseQueryRunner):
    @classmethod
    def name(cls):
        return "Custom JSON with User Context"

    @classmethod
    def type(cls):
        return "custom_json_api"

    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {
                "default_url": {
                    "type": "string",
                    "title": "Base URL (used if not overridden in query)",
                }
            },
            "required": [],
        }

    def run_query(self, query, user=None):
        try:
            query_data = json.loads(query)
            url = query_data.get("url", self.configuration.get("default_url"))

            if not url:
                return None, "URL is required in either query YAML or data source config."

            headers = query_data.get("headers", {})
            params = query_data.get("params", {})

            # Inject Redash user email
            if user and hasattr(user, "email"):
                headers["X-Redash-User-Email"] = user.email
                params["user_email"] = user.email

            response = requests.get(url, headers=headers, params=params)
            print("📥 Raw Response:", response.status_code, response.text)

            response.raise_for_status()
            result = response.json()

            rows = result if isinstance(result, list) else [result]
            if not rows:
                return json_dumps({"columns": [], "rows": []}), None

            columns = [{"name": k, "friendly_name": k, "type": "string"} for k in rows[0].keys()]
            return json_dumps({"columns": columns, "rows": rows}), None

        except Exception as e:
            return None, f"CustomJsonAPI error: {str(e)}"
