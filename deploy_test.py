"""
Simple test file to verify deployment
"""
import sys
import platform

def main():
    print(f"✅ Python version: {sys.version}")
    print(f"✅ Platform: {platform.platform()}")
    print("✅ Deployment test successful!")

if __name__ == "__main__":
    main()