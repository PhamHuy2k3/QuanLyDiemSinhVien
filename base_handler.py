"""Base class for error handling and logging."""
import logging
from typing import Any, Optional, Tuple, Union
from constants_new import StatusCodes, Messages

class BaseHandler:
    def __init__(self):
        """Initialize logging."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler('app.log')
        c_handler.setLevel(logging.WARNING)
        f_handler.setLevel(logging.INFO)
        
        # Create formatters and add to handlers
        log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(log_format)
        f_handler.setFormatter(log_format)
        
        # Add handlers to the logger
        self.logger.addHandler(c_handler)
        self.logger.addHandler(f_handler)

    def handle_error(self, error: Exception, context: str = "") -> Tuple[StatusCodes, str]:
        """Handle errors and log them."""
        error_message = f"{context}: {str(error)}" if context else str(error)
        self.logger.error(error_message)
        return StatusCodes.ERROR, error_message

    def handle_success(self, message: str) -> Tuple[StatusCodes, str]:
        """Handle success messages and log them."""
        self.logger.info(message)
        return StatusCodes.SUCCESS, message

    def validate_input(self, value: Any, validator_func: callable,
                      error_message: str = Messages.INVALID_INPUT) -> Tuple[bool, Optional[str]]:
        """Validate input using provided validator function."""
        try:
            if validator_func(value):
                return True, None
            return False, error_message
        except Exception as e:
            return False, f"{error_message}: {str(e)}"

    def log_action(self, action: str, details: str = "", level: str = "INFO") -> None:
        """Log an action with optional details."""
        log_message = f"{action} - {details}" if details else action
        log_func = getattr(self.logger, level.lower())
        log_func(log_message)

    def format_response(self, status: StatusCodes, message: str,
                       data: Any = None) -> dict:
        """Format response in a consistent way."""
        return {
            "status": status,
            "message": message,
            "data": data
        }
