# telegram-chatbot-admin

This project is a Telegram chatbot with an admin dashboard for managing users and viewing chat history. The bot interacts with users through Telegram, while the web application provides an interface for administrators to manage the chatbot's functionalities.

## Project Structure

```
telegram-chatbot-admin
├── src
│   ├── bot                # Contains the Telegram bot logic
│   │   ├── __init__.py
│   │   ├── handlers       # Handlers for bot commands and messages
│   │   ├── keyboards      # Inline keyboards for user interactions
│   │   └── main.py        # Entry point for the bot
│   ├── web                # Web application for the admin dashboard
│   │   ├── __init__.py
│   │   ├── app.py         # Flask application setup
│   │   ├── routes         # Organizes web routes
│   │   └── templates      # HTML templates for the web application
│   ├── database           # Database connection and models
│   ├── services           # Business logic for user and chat management
│   └── utils              # Utility functions and configuration
├── static                 # Static files (CSS, JS, images)
├── requirements.txt       # Project dependencies
├── .env.example           # Example environment variables
├── .gitignore             # Files to ignore in version control
├── run_bot.py             # Script to run the Telegram bot
└── run_web.py             # Script to run the web application
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd telegram-chatbot-admin
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables by copying `.env.example` to `.env` and filling in the required values.

## Migration the database
python -m src.database.migrations.init_db

## recreate the table
python -m src.database.migrations.recreate_tables
## create super admin
python -m src.database.migrations.seed_super_admin
## create categories
python -m src.database.migrations.seed_categories
## create faqs
python -m src.database.migrations.seed_faqs













## Running the Bot

To run the Telegram bot, execute the following command:
```
python run_bot.py
```

## Running the Web Application

To run the admin dashboard, execute the following command:
```
python run_web.py
```

## Usage

- Use the Telegram bot to interact with users and manage chat sessions.
- Access the admin dashboard through a web browser to view user lists and chat history.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.