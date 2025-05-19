import pytest
from unittest.mock import patch, MagicMock
import demo
import sys
import subprocess
import webbrowser
import time

@pytest.fixture
def mock_subprocess():
    with patch('subprocess.Popen') as mock:
        yield mock

@pytest.fixture
def mock_webbrowser():
    with patch('webbrowser.open') as mock:
        yield mock

@pytest.fixture
def mock_time():
    with patch('time.sleep') as mock:
        # Make sleep return immediately
        mock.return_value = None
        yield mock

@pytest.fixture
def mock_print():
    with patch('builtins.print') as mock:
        yield mock

def test_start_server_windows(mock_subprocess):
    """Test server start on Windows platform"""
    with patch('sys.platform', 'win32'):
        old = getattr(subprocess, "CREATE_NEW_CONSOLE", None)
        subprocess.CREATE_NEW_CONSOLE = 0x08000000
        try:
            demo.start_server()
            mock_subprocess.assert_called_once_with(
                ['uvicorn', 'main:app', '--reload'],
                creationflags=0x08000000
            )
        finally:
            if old is not None:
                subprocess.CREATE_NEW_CONSOLE = old
            else:
                delattr(subprocess, "CREATE_NEW_CONSOLE")

def test_start_server_unix(mock_subprocess):
    """Test server start on Unix-like platforms"""
    with patch('sys.platform', 'linux'):
        demo.start_server()
        mock_subprocess.assert_called_once_with(
            ['uvicorn', 'main:app', '--reload']
        )

def test_open_browser_windows(mock_webbrowser, mock_time):
    """Test opening browser windows"""
    demo.open_browser_windows()
    
    # Should open 4 browser windows with delays
    assert mock_webbrowser.call_count == 4
    assert mock_time.call_count == 4
    
    # Verify all calls were made with the correct URL
    for call in mock_webbrowser.call_args_list:
        assert call[0][0] == 'http://localhost:8000'

def test_main_flow(mock_subprocess, mock_webbrowser, mock_time, mock_print):
    """Test the main function flow"""
    with patch('builtins.input', return_value=''):
        with patch('sys.exit') as mock_exit:
            # Simulate KeyboardInterrupt after a few iterations
            mock_time.side_effect = [None, None, None, None, KeyboardInterrupt()]
            
            demo.main()
            
            # Verify server was started
            mock_subprocess.assert_called_once()
            
            # Verify browser windows were opened
            assert mock_webbrowser.call_count == 4
            
            # Verify exit was called
            mock_exit.assert_called_once_with(0)
            
            # Verify instructions were printed
            assert any("Starting Fantasy Draft Demo" in call[0][0] for call in mock_print.call_args_list)
            assert any("Instructions:" in call[0][0] for call in mock_print.call_args_list)
            assert any("Demo is running!" in call[0][0] for call in mock_print.call_args_list)

def test_main_flow_immediate_exit(mock_subprocess, mock_webbrowser, mock_time, mock_print):
    """Test the main function flow with immediate exit"""
    with patch('builtins.input', return_value=''):
        # Make time.sleep raise SystemExit after browser windows are opened
        mock_time.side_effect = [None, None, None, None, SystemExit()]
        
        with pytest.raises(SystemExit):
            demo.main()
        
        # Verify server was started
        mock_subprocess.assert_called_once()
        
        # Verify browser windows were opened
        assert mock_webbrowser.call_count == 4

def test_main_flow_keyboard_interrupt(mock_subprocess, mock_webbrowser, mock_time, mock_print):
    """Test the main function flow with keyboard interrupt"""
    with patch('builtins.input', return_value=''):
        with patch('sys.exit') as mock_exit:
            # Simulate keyboard interrupt after a few iterations
            mock_time.side_effect = [None, None, None, None, KeyboardInterrupt()]
            
            demo.main()
            
            # Verify server was started
            mock_subprocess.assert_called_once()
            
            # Verify browser windows were opened
            assert mock_webbrowser.call_count == 4
            
            # Verify exit message was printed
            assert any("Stopping server" in call[0][0] for call in mock_print.call_args_list) 