from flask import Response, jsonify


class ResponseBuilder:

    @classmethod
    def raw(cls, dict, headers=[]):
        return Response(dict, headers=headers), 201

    @classmethod
    def error_404(cls, url=""):
        return (
            jsonify(
                {
                    "error": "No results found. Check url again",
                    "url": url,
                }
            ),
            200,
        )

    @classmethod
    def error_403(cls, url=""):
        return (
            jsonify(
                {
                    "error": "Not authorized",
                    "url": url,
                }
            ),
            403,
        )

    @classmethod
    def error_500(cls, msg, url=""):
        return (
            jsonify({"error": "Operation not permited", "url": url, "msg": msg}),
            500,
        )

    @classmethod
    def data_removed(cls, desc):
        return (
            jsonify({"message": f"Record {desc} removed"}),
            200,
        )

    @classmethod
    def ok(cls, desc):
        return (
            jsonify({"message": desc}),
            200,
        )

    @classmethod
    def error_parse(cls, err):
        return (
            jsonify(
                {
                    "error": "Validation Error",
                    "messages": err.messages,
                    # "valid_data": err.valid_data,
                }
            ),
            400,
        )

    @classmethod
    def data_list(cls, dict, schema=None):
        if schema:
            return {
                "content": [schema.dump(i) for i in dict["content"]],
                "total_pages": dict["total_pages"],
                "total_elements": dict["total_elements"],
                "per_page": dict["per_page"],
            }
        else:
            return jsonify(dict), 201

    @classmethod
    def data(cls, dict, schema=None):
        if schema:
            return jsonify(schema.dump(dict)), 201
        else:
            return jsonify(dict), 201
