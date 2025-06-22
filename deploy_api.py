"""
Deployment script for Promptsmith API

This script helps deploy the Promptsmith API to various platforms:
- Railway
- Render
- Heroku
- DigitalOcean App Platform
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def create_procfile():
    """Create Procfile for Heroku deployment"""
    with open("Procfile", "w") as f:
        f.write("web: uvicorn api_server:app --host=0.0.0.0 --port=$PORT\n")

def create_runtime_txt():
    """Create runtime.txt for Python version specification"""
    with open("runtime.txt", "w") as f:
        f.write("python-3.11.0\n")

def create_railway_json():
    """Create railway.json for Railway deployment"""
    config = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "uvicorn api_server:app --host=0.0.0.0 --port=$PORT",
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10
        }
    }
    with open("railway.json", "w") as f:
        json.dump(config, f, indent=2)

def create_render_yaml():
    """Create render.yaml for Render deployment"""
    config = {
        "services": [
            {
                "type": "web",
                "name": "promptsmith-api",
                "env": "python",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "uvicorn api_server:app --host=0.0.0.0 --port=$PORT",
                "envVars": [
                    {
                        "key": "OPENAI_API_KEY",
                        "value": "your-openai-api-key-here"
                    }
                ]
            }
        ]
    }
    with open("render.yaml", "w") as f:
        import yaml
        yaml.dump(config, f, default_flow_style=False)

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these before deployment.")
        return False
    
    return True

def test_api_locally():
    """Test the API locally before deployment"""
    print("🧪 Testing API locally...")
    try:
        # Start the server in background
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "api_server:app", 
            "--host", "0.0.0.0", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        import time
        time.sleep(3)
        
        # Test the health endpoint
        import requests
        response = requests.get("http://localhost:8000/")
        
        if response.status_code == 200:
            print("✅ API test successful!")
        else:
            print(f"❌ API test failed: {response.status_code}")
        
        # Stop the server
        process.terminate()
        process.wait()
        
    except Exception as e:
        print(f"❌ API test failed: {e}")

def main():
    """Main deployment setup function"""
    print("🚀 Setting up Promptsmith API for deployment...")
    
    # Check environment
    if not check_environment():
        print("Please set required environment variables and try again.")
        return
    
    # Create deployment files
    print("📝 Creating deployment configuration files...")
    create_procfile()
    create_runtime_txt()
    create_railway_json()
    create_render_yaml()
    
    # Test locally
    test_api_locally()
    
    print("\n🎉 Deployment setup complete!")
    print("\n📋 Next steps:")
    print("1. Choose your deployment platform:")
    print("   - Railway: railway.app")
    print("   - Render: render.com")
    print("   - Heroku: heroku.com")
    print("   - DigitalOcean: digitalocean.com")
    print("\n2. Set environment variables on your platform:")
    print("   - OPENAI_API_KEY")
    print("\n3. Deploy using your platform's CLI or dashboard")
    print("\n4. Update your website's API endpoint to point to the deployed URL")

if __name__ == "__main__":
    main() 