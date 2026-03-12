# Contributing to Canon Shutter Counter Pro

Thank you for your interest in contributing to this project!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/canon-shutter-counter.git
   cd canon-shutter-counter
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python CanonShutterCounter.py
   ```

## Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and modular

## Testing

Before submitting changes:
1. Test the application with real CR3 files
2. Test USB camera detection (if possible)
3. Test both dark and light modes
4. Ensure the build process still works (`build_simple.bat`)

## Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a Pull Request

## Reporting Bugs

Please include:
- Operating System and version
- Python version (if applicable)
- Steps to reproduce the issue
- Expected vs actual behavior
- Screenshots (if relevant)

## Feature Requests

Feel free to open an issue to discuss new features or improvements!

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE.txt).

