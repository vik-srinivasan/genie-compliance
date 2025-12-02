"""
Run the contract safety chatbot web server.
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.web.app import app

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5001))
    print("=" * 60)
    print("Starting Contract Safety Chatbot...")
    print("=" * 60)
    print(f"Open your browser to: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=port)

