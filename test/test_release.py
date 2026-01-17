import sys
from pathlib import Path
import logging

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports():
    print("Testing Imports...")
    
    # Test core dependencies
    try:
        import pystray
        print("✅ pystray imported")
    except ImportError as e:
        print(f"❌ pystray import failed: {e}")
        return False

    try:
        from PIL import Image
        print("✅ pillow imported")
    except ImportError as e:
        print(f"❌ pillow import failed: {e}")
        return False

    # Test Application Modules
    try:
        import tray_app
        print("✅ tray_app imported")
    except ImportError as e:
        print(f"❌ tray_app import failed: {e}")
        return False

    try:
        import annotes
        print("✅ annotes imported")
        
        # Test In-Memory Logging
        print("Testing Logging...")
        annotes.setup_logging()
        logging.info("Test Log Entry 1")
        logging.info("Test Log Entry 2")
        
        logs = annotes.get_recent_logs()
        if len(logs) >= 2:
            print(f"✅ In-memory buffer working. Count: {len(logs)}")
        else:
            print(f"❌ In-memory buffer empty or low: {len(logs)}")
            return False
            
    except ImportError as e:
        print(f"❌ annotes import failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    if test_imports():
        print("\nRelease Candidate Verified.")
        sys.exit(0)
    else:
        print("\nVerification Failed.")
        sys.exit(1)
