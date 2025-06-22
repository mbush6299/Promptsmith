#!/usr/bin/env python3
"""
Railway deployment helper for Promptsmith
"""

import os
import subprocess
import sys

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI is installed")
            return True
        else:
            print("❌ Railway CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI not found")
        return False

def install_railway_cli():
    """Install Railway CLI"""
    print("📦 Installing Railway CLI...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'railway'], check=True)
        print("✅ Railway CLI installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Railway CLI: {e}")
        return False

def deploy_to_railway():
    """Deploy to Railway"""
    print("🚀 Deploying to Railway...")
    
    # Check if already logged in
    try:
        result = subprocess.run(['railway', 'whoami'], capture_output=True, text=True)
        if result.returncode != 0:
            print("🔐 Please login to Railway first:")
            print("   railway login")
            return False
    except:
        print("🔐 Please login to Railway first:")
        print("   railway login")
        return False
    
    # Initialize project if not already done
    if not os.path.exists('.railway'):
        print("📁 Initializing Railway project...")
        subprocess.run(['railway', 'init'], check=True)
    
    # Deploy
    print("🚀 Deploying...")
    subprocess.run(['railway', 'up'], check=True)
    
    # Get the URL
    print("🔗 Getting deployment URL...")
    result = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
    if result.returncode == 0:
        domain = result.stdout.strip()
        print(f"✅ Deployed successfully!")
        print(f"🌐 Your API URL: https://{domain}")
        print(f"\n📋 Next steps:")
        print(f"1. Set environment variables in Railway dashboard:")
        print(f"   - OPENAI_API_KEY: your-openai-api-key")
        print(f"2. Update your website's PROMPTSMITH_API_URL to: https://{domain}")
        return domain
    else:
        print("❌ Failed to get deployment URL")
        return None

def main():
    """Main deployment function"""
    print("🚀 Railway Deployment Helper for Promptsmith")
    print("=" * 50)
    
    # Check Railway CLI
    if not check_railway_cli():
        install = input("Install Railway CLI? (y/n): ").lower().strip()
        if install == 'y':
            if not install_railway_cli():
                return
        else:
            print("Please install Railway CLI manually: npm install -g @railway/cli")
            return
    
    # Check environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not set")
        print("You'll need to set this in the Railway dashboard after deployment")
    
    # Deploy
    domain = deploy_to_railway()
    
    if domain:
        print(f"\n🎉 Success! Your Promptsmith API is deployed at:")
        print(f"   https://{domain}")
        print(f"\n📝 Don't forget to:")
        print(f"1. Set OPENAI_API_KEY in Railway dashboard")
        print(f"2. Update your website's environment variables")
        print(f"3. Test the integration!")

if __name__ == "__main__":
    main() 