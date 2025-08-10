#!/usr/bin/env python3
"""
NebulAI Mining Script with Automatic JWT Token Refresh & Enhanced Logging
WARNING: This script is for EDUCATIONAL PURPOSES ONLY.
Using automation with NebulAI violates their Terms of Service and may result in account termination.
"""

import hashlib
import time
import random
import aiohttp
import asyncio
import numpy as np
import os
import json
import base64
import logging
from typing import List, Optional, Tuple, Dict
import concurrent.futures
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import jwt
from pathlib import Path
from colorama import Fore, Back, Style, init
import colorama

# Initialize colorama for Windows/Linux compatibility
colorama.init(autoreset=True)

class MiningStats:
    """Global statistics tracker for mining operations"""
    def __init__(self):
        self.session_start = time.time()
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.active_tokens = 0
        self.total_hash_power = 0
        self.last_stats_display = 0
        
    def get_runtime(self) -> str:
        """Get formatted runtime"""
        elapsed = time.time() - self.session_start
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        total = self.tasks_completed + self.tasks_failed
        return (self.tasks_completed / total * 100) if total > 0 else 0
    
    def log_stats(self):
        """Display real-time mining statistics"""
        success_rate = self.get_success_rate()
        runtime = self.get_runtime()
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}⚡ MINING DASHBOARD ⚡")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.GREEN}🕐 Runtime: {runtime}")
        print(f"{Fore.GREEN}🎯 Active Tokens: {self.active_tokens}")
        print(f"{Fore.GREEN}✅ Tasks Completed: {self.tasks_completed}")
        print(f"{Fore.RED}❌ Tasks Failed: {self.tasks_failed}")
        print(f"{Fore.YELLOW}📊 Success Rate: {success_rate:.1f}%")
        print(f"{Fore.MAGENTA}⚡ Hash Power: {self.total_hash_power:.2f} MH/s")
        print(f"{Fore.CYAN}{'='*60}\n")

# Global stats instance
stats = MiningStats()

def print_header():
    print(f"""
{Fore.CYAN}🚀 NebulAI Mining Script v2.0.1{Style.RESET_ALL}
{Fore.CYAN}========================================================{Style.RESET_ALL}


{Fore.GREEN}██████╗  ██  ██████╗ ██╗   ██╗   ████████╗███╗   ███╗{Style.RESET_ALL}
{Fore.GREEN}██╔══██╗ ╔═╗ ██╔══██╗╚██╗ ██╔╝   ╚══██╔══╝████╗ ████║{Style.RESET_ALL}
{Fore.GREEN}██║  ██║ ██║ ██████╔╝ ╚████╔╝       ██║   ██║╚██╔╝██║{Style.RESET_ALL}
{Fore.GREEN}██║  ██║ ██║ ██╔═══╝   ╚██╔╝        ██║   ██║ ╚═╝ ██║{Style.RESET_ALL}
{Fore.GREEN}██║  ██║ ██║ ██║        ██║         ╚═╝   ╚═╝     ╚═╝{Style.RESET_ALL}
{Fore.GREEN}██████╔╝ ██║ ██║        ██║           			     {Style.RESET_ALL}
{Fore.GREEN}╚═════╝  ╚═╝ ╚═╝        ╚═╝						     {Style.RESET_ALL}  

{Fore.YELLOW}               Created by DiPY™                     {Style.RESET_ALL}
   
{Fore.CYAN}========================================================{Style.RESET_ALL}
""")

def print_mining_header():
    """Display mining operation start header"""
    print(f"{Fore.GREEN}🚀 {Style.BRIGHT}INITIALIZING MINING OPERATIONS...")
    print(f"{Fore.YELLOW}⚠️  {Style.BRIGHT}WARNING: This script violates NebulAI ToS - Use at your own risk!")
    print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

def print_mining_footer():
    """Display mining operation end footer"""
    print(f"\n{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"{Fore.YELLOW}⛔ {Style.BRIGHT}MINING OPERATIONS TERMINATED")
    print(f"{Fore.GREEN}💎 NebulAI Miner - DiPY™")
    stats.log_stats()
    print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

class ColoredFormatter(logging.Formatter):
    """Custom colored formatter for mining operations"""
    
    # Mining-themed icons and colors
    FORMATS = {
        logging.DEBUG: f"{Fore.LIGHTBLACK_EX}🔍 [DEBUG] %(message)s",
        logging.INFO: f"{Fore.GREEN}⚡ [INFO] %(message)s", 
        logging.WARNING: f"{Fore.YELLOW}⚠️  [WARN] %(message)s",
        logging.ERROR: f"{Fore.RED}❌ [ERROR] %(message)s",
        logging.CRITICAL: f"{Fore.RED}{Back.WHITE}💥 [CRITICAL] %(message)s"
    }

    def format(self, record):
        # Add timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Get the appropriate format
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(f"{Fore.CYAN}[{timestamp}] {log_fmt}{Style.RESET_ALL}")
        
        # Format the message with mining context
        original_msg = record.getMessage()
        
        # Enhance specific message types
        if "Task received" in original_msg:
            record.msg = f"📥 New mining task acquired - {original_msg.split('Task received')[1]}"
        elif "Results accepted" in original_msg:
            record.msg = f"✅ Mining reward earned - {original_msg.split('Results accepted')[1]}"
            stats.tasks_completed += 1
        elif "Results rejected" in original_msg:
            record.msg = f"❌ Mining task failed - {original_msg.split('Results rejected')[1]}"
            stats.tasks_failed += 1
        elif "Starting worker" in original_msg:
            record.msg = f"🚀 Mining rig online - {original_msg.split('Starting worker')[1]}"
        elif "Token refreshed" in original_msg:
            record.msg = f"🔄 Authentication renewed - Token updated successfully"
        elif "Fetch error" in original_msg:
            record.msg = f"🌐 Network issue - {original_msg.split('Fetch error')[1]}"
        
        return formatter.format(record)

# ===============================
# WARNING: TERMS OF SERVICE VIOLATION
# ===============================
print_header()
print(f"""
{Fore.RED}{Style.BRIGHT}⚠️  CRITICAL WARNING ⚠️{Style.RESET_ALL}
{Fore.YELLOW}This script violates NebulAI's Terms of Service which explicitly prohibit:
- Automation attempts
- Multiple accounts  
- Gaming the mining system

{Fore.RED}Using this script may result in:
- Permanent account suspension
- Loss of all accumulated rewards
- Legal action for ToS violation

{Fore.CYAN}Proceed at your own risk!{Style.RESET_ALL}
""")

# Load environment variables
load_dotenv()

# Configure enhanced logging
logger = logging.getLogger('NebulAI_Miner')
logger.setLevel(logging.INFO)

# Remove existing handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Console handler with colors
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter())
logger.addHandler(console_handler)

# File handler for persistent logs
file_handler = logging.FileHandler('nebulai_mining.log')
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

class SecureTokenManager:
    """Manages JWT tokens with automatic refresh and secure storage"""
    
    def __init__(self):
        self.tokens_file = Path("tokens.txt")
        self.private_key = self._load_private_key()
        self.encryption_key = self._get_or_create_encryption_key()
        self.token_refresh_hours = 23  # Refresh 1 hour before expiry
        self.last_refresh = {}
        
    def _load_private_key(self) -> Optional[str]:
        """Load Solana private key from environment"""
        private_key = os.getenv('SOLANA_PRIVATE_KEY')
        if not private_key:
            logger.error("SOLANA_PRIVATE_KEY not found in .env file!")
            return None
        return private_key
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for token storage"""
        key_file = Path(".token_encryption_key")
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict file permissions
            return key
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt JWT token for secure storage"""
        f = Fernet(self.encryption_key)
        return f.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt JWT token"""
        f = Fernet(self.encryption_key)
        return f.decrypt(encrypted_token.encode()).decode()
    
    def is_token_expired(self, token: str) -> bool:
        """Check if JWT token is expired or near expiry"""
        try:
            # Decode without verification to check expiry
            payload = jwt.decode(token, options={"verify_signature": False})
            exp = payload.get('exp')
            if not exp:
                return True
            
            # Check if token expires within next hour
            expiry_time = datetime.fromtimestamp(exp)
            buffer_time = datetime.now() + timedelta(hours=1)
            
            return expiry_time <= buffer_time
        except Exception as e:
            logger.error(f"Error checking token expiry: {e}")
            return True
    
    async def refresh_token(self, old_token: str) -> Optional[str]:
        """
        Refresh JWT token using Solana wallet signature
        NOTE: This is a theoretical implementation as NebulAI's actual API is not documented
        """
        if not self.private_key:
            logger.error("Cannot refresh token without private key")
            return None
        
        try:
            # WARNING: This is a hypothetical implementation
            # NebulAI does not provide public API documentation
            
            # Step 1: Get authentication challenge (hypothetical endpoint)
            async with aiohttp.ClientSession() as session:
                # This would typically request a challenge message to sign
                challenge_url = "https://nebulai.network/api/auth/challenge"
                async with session.get(challenge_url) as resp:
                    if resp.status != 200:
                        logger.error(f"Failed to get auth challenge: {resp.status}")
                        return None
                    challenge_data = await resp.json()
                
                # Step 2: Sign the challenge with Solana private key
                # In reality, this would use solana-py or similar library
                # to create a proper Ed25519 signature
                message = challenge_data.get('message', '')
                timestamp = int(time.time())
                
                # Hypothetical signature creation
                signature_data = {
                    "message": message,
                    "timestamp": timestamp,
                    "signature": "base64_encoded_signature_here",
                    "publicKey": "your_public_key_here"
                }
                
                # Step 3: Submit signature to get new JWT token
                verify_url = "https://nebulai.network/api/auth/verify"
                async with session.post(verify_url, json=signature_data) as resp:
                    if resp.status != 200:
                        logger.error(f"Failed to verify signature: {resp.status}")
                        return None
                    
                    token_data = await resp.json()
                    new_token = token_data.get('token')
                    
                    if new_token:
                        logger.info("Successfully refreshed JWT token")
                        return new_token
                    else:
                        logger.error("No token in refresh response")
                        return None
                        
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None
    
    async def get_valid_tokens(self) -> List[str]:
        """Get all valid tokens, refreshing expired ones"""
        if not self.tokens_file.exists():
            logger.error("tokens.txt not found!")
            return []
        
        valid_tokens = []
        updated_tokens = []
        
        with open(self.tokens_file, 'r') as f:
            tokens = [line.strip() for line in f if line.strip()]
        
        for token in tokens:
            if self.is_token_expired(token):
                logger.info(f"Token {token[:8]}... is expired, attempting refresh")
                new_token = await self.refresh_token(token)
                if new_token:
                    valid_tokens.append(new_token)
                    updated_tokens.append(new_token)
                else:
                    logger.warning(f"Failed to refresh token {token[:8]}...")
                    # Keep the old token in case refresh failed
                    valid_tokens.append(token)
                    updated_tokens.append(token)
            else:
                valid_tokens.append(token)
                updated_tokens.append(token)
        
        # Update tokens file with refreshed tokens
        with open(self.tokens_file, 'w') as f:
            for token in updated_tokens:
                f.write(f"{token}\n")
        
        return valid_tokens

class NebulAIMiner:
    """Main mining class with improved error handling and monitoring"""
    
    def __init__(self, token_manager: SecureTokenManager):
        self.token_manager = token_manager
        self.session_stats = {}
        self.consecutive_failures = {}
        self.max_consecutive_failures = 5
        
    def generate_matrix(self, seed: int, size: int) -> np.ndarray:
        """Generate matrix for computation task"""
        matrix = np.empty((size, size), dtype=np.float64)
        current_seed = seed
        a, b = 0x4b72e682d, 0x2675dcd22
        for i in range(size):
            for j in range(size):
                value = (a * current_seed + b) % 1000
                matrix[i][j] = float(value)
                current_seed = value
        return matrix

    def multiply_matrices(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Multiply two matrices"""
        return a @ b

    def flatten_matrix(self, matrix: np.ndarray) -> str:
        """Flatten matrix to string"""
        return ''.join(f"{x:.0f}" for x in matrix.flat)

    async def compute_hash_mod(self, matrix: np.ndarray, mod: int = 10**7) -> int:
        """Compute hash modulo of flattened matrix"""
        flat_str = self.flatten_matrix(matrix)
        sha256 = hashlib.sha256(flat_str.encode()).hexdigest()
        return int(int(sha256, 16) % mod)

    async def fetch_task(self, session: aiohttp.ClientSession, token: str) -> Tuple[dict, bool]:
        """Fetch new task from server with retry logic"""
        headers = {"Content-Type": "application/json", "token": token}
        
        for attempt in range(3):  # Retry up to 3 times
            try:
                url = "https://nebulai.network/open_compute/finish/task"
                async with session.post(url, json={}, headers=headers, timeout=10) as resp:
                    data = await resp.json()
                    
                    if data.get("code") == 0:
                        logger.info(f"Task received for token {token[:8]}... (matrix size: {data['data']['matrix_size']})")
                        self.consecutive_failures[token] = 0
                        return data['data'], True
                    elif resp.status == 401:
                        logger.warning(f"Authentication failed for token {token[:8]}... - token may be expired")
                        return None, False
                    else:
                        logger.warning(f"Unexpected response for token {token[:8]}...: {data}")
                        
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching task for token {token[:8]}... (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Fetch error for token {token[:8]}...: {str(e)}")
                
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
                
        return None, False

    async def submit_results(self, session: aiohttp.ClientSession, token: str, 
                           r1: float, r2: float, task_id: str) -> bool:
        """Submit computation results with retry logic"""
        headers = {"Content-Type": "application/json", "token": token}
        payload = {
            "result_1": f"{r1:.10f}", 
            "result_2": f"{r2:.10f}", 
            "task_id": task_id
        }
        
        for attempt in range(3):
            try:
                url = "https://nebulai.network/open_compute/finish/task"
                async with session.post(url, json=payload, headers=headers, timeout=10) as resp:
                    data = await resp.json()
                    
                    if data.get("code") == 0 and data.get("data", {}).get("calc_status", False):
                        logger.info(f"Results accepted for token {token[:8]}...")
                        self._update_stats(token, True)
                        return True
                    else:
                        logger.warning(f"Results rejected for token {token[:8]}...: {data}")
                        
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        
            except Exception as e:
                logger.error(f"Submit error for token {token[:8]}...: {str(e)}")
                
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
                
        self._update_stats(token, False)
        return False

    async def process_task(self, token: str, task_data: dict) -> Optional[Tuple[float, float]]:
        """Process computation task"""
        seed1, seed2, size = task_data["seed1"], task_data["seed2"], task_data["matrix_size"]
        
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                t0 = time.time() * 1000
                
                # Generate matrices in parallel
                A_future = executor.submit(self.generate_matrix, seed1, size)
                B_future = executor.submit(self.generate_matrix, seed2, size)
                
                A, B = await asyncio.gather(
                    asyncio.wrap_future(A_future),
                    asyncio.wrap_future(B_future)
                )
                
            # Multiply matrices
            C = self.multiply_matrices(A, B)
            
            # Compute hash
            f = await self.compute_hash_mod(C)
            t1 = time.time() * 1000
            
            result_1 = t0 / f
            result_2 = f / (t1 - t0) if (t1 - t0) != 0 else 0
            
            # Update hash power stats
            stats.total_hash_power = f / 1000000  # Convert to MH/s
            
            return result_1, result_2
            
        except Exception as e:
            logger.error(f"Computation error: {str(e)}")
            return None

    def _update_stats(self, token: str, success: bool):
        """Update session statistics"""
        if token not in self.session_stats:
            self.session_stats[token] = {"success": 0, "failure": 0, "start_time": time.time()}
        
        if success:
            self.session_stats[token]["success"] += 1
        else:
            self.session_stats[token]["failure"] += 1
            self.consecutive_failures[token] = self.consecutive_failures.get(token, 0) + 1

    async def worker_loop(self, token: str):
        """Main worker loop for a single token"""
        logger.info(f"Starting worker for token {token[:8]}...")
        
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    # Check if token needs refresh
                    if self.token_manager.is_token_expired(token):
                        logger.info(f"Token {token[:8]}... needs refresh")
                        new_token = await self.token_manager.refresh_token(token)
                        if new_token:
                            token = new_token
                            logger.info("Token refreshed successfully")
                        else:
                            logger.error(f"Failed to refresh token {token[:8]}...")
                            await asyncio.sleep(60)  # Wait before retry
                            continue
                    
                    # Check consecutive failures
                    if self.consecutive_failures.get(token, 0) >= self.max_consecutive_failures:
                        logger.error(f"Too many consecutive failures for token {token[:8]}..., pausing worker")
                        await asyncio.sleep(300)  # 5 minute cooldown
                        self.consecutive_failures[token] = 0
                        continue
                    
                    # Fetch task
                    task_data, success = await self.fetch_task(session, token)
                    if not success:
                        await asyncio.sleep(3)
                        continue
                    
                    # Process task
                    results = await self.process_task(token, task_data)
                    if not results:
                        await asyncio.sleep(1)
                        continue
                    
                    # Submit results
                    submitted = await self.submit_results(session, token, results[0], results[1], task_data["task_id"])
                    
                    # Show stats periodically
                    current_time = time.time()
                    if current_time - stats.last_stats_display > 300:  # Every 5 minutes
                        stats.log_stats()
                        stats.last_stats_display = current_time
                    
                    # Adaptive delay based on success
                    if submitted:
                        await asyncio.sleep(0.5)
                    else:
                        await asyncio.sleep(3)
                    
                except Exception as e:
                    logger.error(f"Unexpected error in worker loop: {str(e)}")
                    await asyncio.sleep(10)

    def print_final_stats(self):
        """Print final mining statistics"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}📊 FINAL MINING REPORT")
        print(f"{Fore.CYAN}{'='*60}")
        
        for token, session_stats in self.session_stats.items():
            runtime = time.time() - session_stats["start_time"]
            success_rate = session_stats["success"] / (session_stats["success"] + session_stats["failure"]) * 100 if (session_stats["success"] + session_stats["failure"]) > 0 else 0
            
            print(f"\n{Fore.MAGENTA}Token: {token[:8]}...")
            print(f"  {Fore.GREEN}✅ Success: {session_stats['success']}")
            print(f"  {Fore.RED}❌ Failure: {session_stats['failure']}")
            print(f"  {Fore.YELLOW}📈 Success Rate: {success_rate:.1f}%")
            print(f"  {Fore.CYAN}⏱️  Runtime: {runtime/3600:.1f} hours")

async def main():
    """Main entry point"""
    print_mining_header()
    
    # Check for required files
    if not os.path.exists(".env"):
        logger.error(".env file not found! Create it with SOLANA_PRIVATE_KEY=your_key")
        return
    
    # Initialize token manager
    token_manager = SecureTokenManager()
    
    # Get valid tokens
    tokens = await token_manager.get_valid_tokens()
    if not tokens:
        logger.error("No valid tokens found!")
        return
    
    # Update global stats
    stats.active_tokens = len(tokens)
    
    logger.info(f"🎯 Initialized {len(tokens)} machine")
    
    # Initialize miner
    miner = NebulAIMiner(token_manager)
    
    # Create tasks for all tokens
    tasks = [miner.worker_loop(token) for token in tokens]
    
    # Add periodic stats display
    async def stats_display_loop():
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            stats.log_stats()
    
    tasks.append(stats_display_loop())
    
    # Add token refresh scheduler
    async def token_refresh_scheduler():
        while True:
            await asyncio.sleep(3600)  # Check every hour
            logger.info("🔄 Running scheduled token refresh check")
            await token_manager.get_valid_tokens()
    
    tasks.append(token_refresh_scheduler())
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("⛔ Mining stopped by user")
        miner.print_final_stats()
        print_mining_footer()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_mining_footer()
        print(f"{Fore.CYAN}👋 NebulAI Miner v2.0.1 - DiPY™")