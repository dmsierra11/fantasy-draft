# Fantasy Sports Draft System

A real-time fantasy sports draft application built with FastAPI that enables multiple teams to conduct a snake draft format selection process.

## Features

- 🎯 Real-time draft updates using WebSockets
- 🔄 Snake draft format (order reverses each round)
- 📱 RESTful API endpoints for draft management
- 🎮 Simple and intuitive draft flow
- 🔔 Real-time notifications to all connected clients

## Prerequisites

- Python 3.7+
- FastAPI
- WebSocket support
- pytest (for testing)
- flake8 (for linting)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fantasy-draft.git
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
- `test_main.py`: Main application tests
- `test_ws.py`: WebSocket testing utilities
- `requirements.txt`: Project dependencies
- `pyproject.toml`: Project configuration
- `.coveragerc`: Coverage configuration
- `.github/`: GitHub workflows and templates
- `.vscode/`: VS Code configuration

## API Endpoints

### REST Endpoints

- `GET /start_draft`: Initialize a new draft
- `GET /get_status`: Get current draft status
- `POST /pick_player/{team}/{player}`: Make a player selection

### WebSocket

- `WS /ws`: Connect for real-time draft updates

## Draft Rules

- Teams are randomly ordered at the start
- Each team gets one pick per round
- The order reverses each round (snake draft format)
- Players can only be picked once
- Teams can only pick when it's their turn

## Sample Setup

- 4 teams (Team A through D)
- 20 sample players
- 5 rounds of drafting

## Development

The project is structured as follows:
- `main.py`: Core application logic and API endpoints
- `test_ws.py`: WebSocket testing utilities

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

This project is licensed under the MIT License - see the LICENSE file for details. 