#!/usr/bin/env python3
"""
NebulAI Mining Setup Health Check
Validates configuration before running the miner
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import importlib.util

class HealthChecker:
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.critical_failure = False
        
    def check(self, condition: bool, success_msg: str, failure_msg: str, critical: bool = False):
        """Run a single health check"""
        if condition:
            print(f"✅ {success_msg}")
            self.checks_passed += 1
        else:
            print(f"❌ {failure_msg}")
            self.checks_failed += 1
            if critical:
                self.critical_failure = True
                
    def check_python_version(self):
        """Check Python version compatibility"""
        version = sys.version_info
        self.check(
            version.major == 3 and version.minor >= 8,
            f"Python version {version.major}.{version.minor} is supported",
            f"Python version {version.major}.{version.minor} is not supported (need 3.8+)",
            critical=True
        )
        
    def check_dependencies(self):
        """Check if required packages are installed"""
        required_packages = [
            ('aiohttp', 'aiohttp'),
            ('numpy', 'numpy'),
            ('cryptography', 'cryptography'),
            ('dotenv', 'python-dotenv'),
            ('jwt', 'PyJWT')
        ]
        
        print("\n📦 Checking dependencies...")
        for import_name, package_name in required_packages:
            spec = importlib.util.find_spec(import_name)
            self.check(
                spec is not None,
                f"{package_name} is installed",
                f"{package_name} is NOT installed - run: pip install {package_name}",
                critical=True
            )
            
    def check_files(self):
        """Check if required files exist"""
        print("\n📁 Checking required files...")
        
        # Check .env file
        env_exists = Path('.env').exists()
        self.check(
            env_exists,
            ".env file exists",
            ".env file NOT found - copy .env.template to .env",
            critical=True
        )
        
        # Check tokens.txt
        tokens_exists = Path('tokens.txt').exists()
        self.check(
            tokens_exists,
            "tokens.txt file exists",
            "tokens.txt NOT found - create it and add your JWT tokens"
        )
        
        if tokens_exists:
            with open('tokens.txt', 'r') as f:
                tokens = [line.strip() for line in f if line.strip()]
            self.check(
                len(tokens) > 0,
                f"Found {len(tokens)} token(s) in tokens.txt",
                "tokens.txt is empty - add at least one JWT token"
            )
            
    def check_environment(self):
        """Check environment variables"""
        print("\n🔧 Checking environment configuration...")
        
        load_dotenv()
        
        # Check Solana private key
        private_key = os.getenv('SOLANA_PRIVATE_KEY')
        self.check(
            private_key is not None and len(private_key) > 0,
            "SOLANA_PRIVATE_KEY is configured",
            "SOLANA_PRIVATE_KEY is NOT set in .env file",
            critical=True
        )
        
        if private_key:
            # Basic validation of key format (base58, typical length)
            self.check(
                len(private_key) > 80 and len(private_key) < 100,
                "Private key appears to be valid format",
                "Private key format looks incorrect (wrong length)"
            )
            
    def check_permissions(self):
        """Check file permissions for security"""
        print("\n🔒 Checking file permissions...")
        
        if os.name != 'nt':  # Not Windows
            env_path = Path('.env')
            if env_path.exists():
                mode = env_path.stat().st_mode & 0o777
                self.check(
                    mode <= 0o600,
                    ".env has secure permissions",
                    f".env has loose permissions ({oct(mode)}) - run: chmod 600 .env"
                )
                
    def check_network(self):
        """Check network connectivity to NebulAI"""
        print("\n🌐 Checking network connectivity...")
        
        try:
            import aiohttp
            import asyncio
            
            async def test_connection():
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get('https://nebulai.network', timeout=5) as resp:
                            return resp.status == 200
                except:
                    return False
                    
            connected = asyncio.run(test_connection())
            self.check(
                connected,
                "Can connect to nebulai.network",
                "Cannot connect to nebulai.network - check internet connection"
            )
        except:
            self.check(
                False,
                "Network test passed",
                "Network test failed - check aiohttp installation"
            )
            
    def run_all_checks(self):
        """Run all health checks"""
        print("🏥 NebulAI Mining Setup Health Check")
        print("=" * 50)
        
        print("\n⚠️  REMINDER: This software violates NebulAI ToS!")
        print("⚠️  Proceed at your own risk!\n")
        
        self.check_python_version()
        self.check_dependencies()
        self.check_files()
        self.check_environment()
        self.check_permissions()
        self.check_network()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 SUMMARY")
        print(f"✅ Passed: {self.checks_passed}")
        print(f"❌ Failed: {self.checks_failed}")
        
        if self.critical_failure:
            print("\n🚫 CRITICAL FAILURES DETECTED - Cannot proceed!")
            print("Fix the issues above before running the miner.")
            return False
        elif self.checks_failed > 0:
            print("\n⚠️  Some checks failed but not critical.")
            print("The miner may run but with reduced functionality.")
            return True
        else:
            print("\n🎉 All checks passed! Ready to mine.")
            print("\nRun the miner with: python nebulai_miner.py")
            return True

def main():
    checker = HealthChecker()
    success = checker.run_all_checks()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()