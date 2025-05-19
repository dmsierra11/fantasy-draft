# Fantasy Sports Draft System

A real-time fantasy sports draft application built with FastAPI that enables multiple teams to conduct a snake draft format selection process.

## Features

- 🎯 Real-time draft updates using WebSockets
- 🔄 Snake draft format (order reverses each round)
- 📱 RESTful API endpoints for draft management
- 🎮 Simple and intuitive draft flow
- 🔔 Real-time notifications to all connected clients
- 👥 Team registration system
- 🎲 Automatic draft order randomization

## Prerequisites

- Python 3.7+
- FastAPI
- WebSocket support
- pytest (for testing)
- flake8 (for linting)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dmsierra11/fantasy-draft.git
cd fantasy-draft
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the server:
```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

## Testing

Run the test suite:
```bash
pytest
```

Run tests with coverage report:
```bash
pytest --cov
```

## Project Structure

- `main.py`: Core application logic and API endpoints
- `demo.py`: Demo implementation and utilities
- `test_main.py`: Main application tests
- `test_demo.py`: Demo implementation tests
- `requirements.txt`: Project dependencies
- `pyproject.toml`: Project configuration
- `.coveragerc`: Coverage configuration
- `.pre-commit-config.yaml`: Pre-commit hooks configuration
- `.github/`: GitHub workflows and templates
- `.vscode/`: VS Code configuration
- `static/`: Static files directory
- `templates/`: Template files directory

## API Endpoints

### REST Endpoints

- `GET /`: Serve the demo page
- `POST /register_team`: Register a new team
- `GET /get_status`: Get current draft status
- `POST /start_draft`: Initialize a new draft
- `POST /pick_player/{team}/{player}`: Make a player selection

### WebSocket

- `WS /ws`: Connect for real-time draft updates

## Draft Rules

- Maximum of 4 teams allowed
- Teams are randomly ordered at the start
- Each team gets one pick per round
- The order reverses each round (snake draft format)
- Players can only be picked once
- Teams can only pick when it's their turn
- 20 sample players available
- 5 rounds of drafting

## Development

The project uses several development tools and practices:
- Pre-commit hooks for code quality
- VS Code configuration for development
- GitHub workflows for CI/CD
- Comprehensive test coverage
- CORS middleware for cross-origin requests

## Future Enhancements

- [ ] User authentication
- [ ] Custom league settings
- [ ] Player statistics and rankings
- [ ] Draft timer
- [ ] Enhanced player pool management
- [ ] Frontend interface
- [ ] Database integration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. 
