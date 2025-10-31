class Helpers:

    @staticmethod
    def format_timestamp(timestamp):
        return timestamp.strftime("%Y-%m-%d %I:%M:%S %p")

    @staticmethod
    def sanitize_input(input_string):
        return input_string.strip()

    @staticmethod
    def paginate(items, page, per_page):
        start = (page - 1) * per_page
        end = start + per_page
        return items[start:end]

    def generate_response_message(success, message):
        return {
            "success": success,
            "message": message
        }