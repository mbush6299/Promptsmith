#!/usr/bin/env python3
"""
Quick deployment script for enhanced Promptsmith API
"""

import subprocess
import sys
import os
import time

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return None

def check_railway_cli():
    """Check if Railway CLI is installed."""
    result = subprocess.run("railway --version", shell=True, capture_output=True, text=True)
    return result.returncode == 0

def main():
    print("🚀 Quick Deploy Enhanced Promptsmith API")
    print("=" * 50)
    
    # Check if Railway CLI is installed
    if not check_railway_cli():
        print("❌ Railway CLI not found")
        print("Installing Railway CLI...")
        install_result = run_command("pip install railway", "Installing Railway CLI")
        if not install_result:
            print("❌ Failed to install Railway CLI")
            return False
    
    # Check if we're in a Railway project
    if not os.path.exists("railway.json"):
        print("❌ Not in a Railway project directory")
        print("Please run this script from your Promptsmith project directory")
        return False
    
    # Login to Railway
    print("\n🔐 Please login to Railway:")
    login_result = run_command("railway login", "Logging into Railway")
    if not login_result:
        print("❌ Failed to login to Railway")
        return False
    
    # Link to project
    print("\n🔗 Linking to Railway project:")
    link_result = run_command("railway link", "Linking to Railway project")
    if not link_result:
        print("❌ Failed to link to Railway project")
        return False
    
    # Deploy
    print("\n🚀 Deploying enhanced API:")
    deploy_result = run_command("railway up", "Deploying to Railway")
    if not deploy_result:
        print("❌ Failed to deploy to Railway")
        return False
    
    print("\n🎉 Deployment completed successfully!")
    print("\n📋 Next steps:")
    print("1. Check your Railway dashboard for the deployment status")
    print("2. Verify environment variables are set:")
    print("   - OPENAI_API_KEY")
    print("   - PROMPTSMITH_API_KEY")
    print("3. Test the enhanced API endpoints")
    print("4. Update your frontend to use the new detailed information")
    
    print("\n🔗 Your enhanced API is available at:")
    print("https://promptsmith-production.up.railway.app")
    
    print("\n🧪 Test the enhanced API:")
    print("curl https://promptsmith-production.up.railway.app/")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 