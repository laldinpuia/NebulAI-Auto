#!/usr/bin/env python3
"""
JWT Token Utility for NebulAI
Check token validity, decode payload, and manage tokens
"""

import jwt
import json
import base64
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import sys

class TokenUtility:
    def __init__(self, tokens_file: str = "tokens.txt"):
        self.tokens_file = Path(tokens_file)
        
    def decode_token_unsafe(self, token: str) -> dict:
        """Decode JWT token without verification (for inspection only)"""
        try:
            # Decode without verification
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except Exception as e:
            return {"error": str(e)}
    
    def check_token_expiry(self, token: str) -> dict:
        """Check token expiration status"""
        payload = self.decode_token_unsafe(token)
        
        if "error" in payload:
            return {"status": "error", "message": payload["error"]}
        
        if "exp" not in payload:
            return {"status": "no_expiry", "message": "Token has no expiration"}
        
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        now = datetime.now()
        
        if exp_datetime <= now:
            return {
                "status": "expired",
                "expired_at": exp_datetime.isoformat(),
                "expired_ago": str(now - exp_datetime)
            }
        else:
            return {
                "status": "valid",
                "expires_at": exp_datetime.isoformat(),
                "expires_in": str(exp_datetime - now)
            }
    
    def analyze_all_tokens(self) -> list:
        """Analyze all tokens in tokens.txt"""
        if not self.tokens_file.exists():
            return []
        
        results = []
        with open(self.tokens_file, 'r') as f:
            tokens = [line.strip() for line in f if line.strip()]
        
        for i, token in enumerate(tokens):
            token_info = {
                "index": i + 1,
                "token_preview": f"{token[:20]}...{token[-20:]}",
                "expiry": self.check_token_expiry(token),
                "payload": self.decode_token_unsafe(token)
            }
            results.append(token_info)
        
        return results
    
    def remove_expired_tokens(self) -> int:
        """Remove expired tokens from tokens.txt"""
        if not self.tokens_file.exists():
            return 0
        
        with open(self.tokens_file, 'r') as f:
            tokens = [line.strip() for line in f if line.strip()]
        
        valid_tokens = []
        removed_count = 0
        
        for token in tokens:
            expiry_info = self.check_token_expiry(token)
            if expiry_info["status"] != "expired":
                valid_tokens.append(token)
            else:
                removed_count += 1
        
        # Rewrite file with only valid tokens
        with open(self.tokens_file, 'w') as f:
            for token in valid_tokens:
                f.write(f"{token}\n")
        
        return removed_count
    
    def add_token(self, token: str) -> bool:
        """Add a new token to tokens.txt"""
        # Validate it's a proper JWT format
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        # Check if token already exists
        existing_tokens = []
        if self.tokens_file.exists():
            with open(self.tokens_file, 'r') as f:
                existing_tokens = [line.strip() for line in f if line.strip()]
        
        if token in existing_tokens:
            return False
        
        # Append new token
        with open(self.tokens_file, 'a') as f:
            f.write(f"{token}\n")
        
        return True

def format_token_info(token_info: dict) -> str:
    """Format token information for display"""
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"Token #{token_info['index']}")
    output.append(f"Preview: {token_info['token_preview']}")
    
    expiry = token_info['expiry']
    if expiry['status'] == 'valid':
        output.append(f"Status: ✅ VALID")
        output.append(f"Expires: {expiry['expires_at']}")
        output.append(f"Time remaining: {expiry['expires_in']}")
    elif expiry['status'] == 'expired':
        output.append(f"Status: ❌ EXPIRED")
        output.append(f"Expired: {expiry['expired_at']}")
        output.append(f"Expired ago: {expiry['expired_ago']}")
    else:
        output.append(f"Status: ⚠️  {expiry['status'].upper()}")
    
    # Show some payload fields
    payload = token_info['payload']
    if 'error' not in payload:
        output.append(f"\nPayload preview:")
        for key in ['iss', 'sub', 'aud', 'iat', 'exp']:
            if key in payload:
                if key in ['iat', 'exp']:
                    # Convert timestamps to readable dates
                    value = datetime.fromtimestamp(payload[key]).isoformat()
                else:
                    value = payload[key]
                output.append(f"  {key}: {value}")
    
    return '\n'.join(output)

def main():
    parser = argparse.ArgumentParser(description='JWT Token Utility for NebulAI')
    parser.add_argument('command', choices=['check', 'clean', 'add', 'decode'],
                       help='Command to execute')
    parser.add_argument('--token', '-t', help='Token to process (for add/decode commands)')
    parser.add_argument('--file', '-f', default='tokens.txt', 
                       help='Token file path (default: tokens.txt)')
    
    args = parser.parse_args()
    
    utility = TokenUtility(args.file)
    
    if args.command == 'check':
        print("🔍 Analyzing all tokens...\n")
        results = utility.analyze_all_tokens()
        
        if not results:
            print(f"❌ No tokens found in {args.file}")
            return
        
        valid_count = sum(1 for r in results if r['expiry']['status'] == 'valid')
        expired_count = sum(1 for r in results if r['expiry']['status'] == 'expired')
        
        print(f"📊 Summary: {len(results)} total tokens")
        print(f"   ✅ Valid: {valid_count}")
        print(f"   ❌ Expired: {expired_count}")
        print(f"   ⚠️  Other: {len(results) - valid_count - expired_count}")
        
        for token_info in results:
            print(format_token_info(token_info))
    
    elif args.command == 'clean':
        print("🧹 Removing expired tokens...")
        removed = utility.remove_expired_tokens()
        print(f"✅ Removed {removed} expired tokens")
    
    elif args.command == 'add':
        if not args.token:
            print("❌ Please provide a token with --token")
            return
        
        if utility.add_token(args.token):
            print("✅ Token added successfully")
            # Check its validity
            expiry = utility.check_token_expiry(args.token)
            if expiry['status'] == 'valid':
                print(f"   Status: VALID (expires: {expiry['expires_at']})")
            else:
                print(f"   Status: {expiry['status'].upper()}")
        else:
            print("❌ Failed to add token (invalid format or already exists)")
    
    elif args.command == 'decode':
        if not args.token:
            print("❌ Please provide a token with --token")
            return
        
        payload = utility.decode_token_unsafe(args.token)
        if 'error' in payload:
            print(f"❌ Error decoding token: {payload['error']}")
        else:
            print("📄 Decoded JWT Payload:")
            print(json.dumps(payload, indent=2, default=str))
            
            # Also show expiry status
            expiry = utility.check_token_expiry(args.token)
            print(f"\n⏰ Expiry Status: {expiry['status'].upper()}")
            if expiry['status'] == 'valid':
                print(f"   Expires in: {expiry['expires_in']}")

if __name__ == "__main__":
    main()