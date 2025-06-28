"""
DexScreener API integration for monitoring Roaring Kitty token.
"""

import asyncio
import logging
import requests
import json
from typing import Callable, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DexScreenerMonitor:
    def __init__(self, token_address: str, notification_callback: Callable):
        """
        Initialize DexScreener monitor for Roaring Kitty token.
        
        Args:
            token_address: The Roaring Kitty token contract address
            notification_callback: Function to call when new buys detected
        """
        self.token_address = token_address.lower()
        self.notification_callback = notification_callback
        self.monitoring = False
        self.last_h24_buys = 0
        self.last_m5_buys = 0
        self.current_data = None
        
        # DexScreener API endpoints
        self.api_base = "https://api.dexscreener.com"
        self.pairs_endpoint = f"{self.api_base}/latest/dex/tokens/{self.token_address}"
        
    async def initialize(self) -> bool:
        """Initialize the monitor and fetch initial data."""
        try:
            logger.info(f"Initializing DexScreener monitor for Roaring Kitty token: {self.token_address}")
            
            # Fetch initial data
            initial_data = await self.fetch_token_data()
            if not initial_data:
                logger.error("Failed to fetch initial token data")
                return False
            
            self.current_data = initial_data
            
            # Set baseline for buy detection
            if initial_data.get('pairs'):
                pair = initial_data['pairs'][0]  # Use first/main pair
                txns = pair.get('txns', {})
                self.last_h24_buys = txns.get('h24', {}).get('buys', 0)
                self.last_m5_buys = txns.get('m5', {}).get('buys', 0)
                
                logger.info(f"Initialized monitoring - Current 24h buys: {self.last_h24_buys}, 5m buys: {self.last_m5_buys}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize DexScreener monitor: {e}")
            return False
    
    async def fetch_token_data(self) -> Optional[Dict]:
        """Fetch current token data from DexScreener API."""
        try:
            response = requests.get(self.pairs_endpoint, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('pairs'):
                logger.warning("No pairs found for token")
                return None
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching token data: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing API response: {e}")
            return None
    
    def get_token_balance_from_pair(self, pair_data: Dict) -> float:
        """Extract token balance/liquidity from pair data."""
        try:
            # Get liquidity in USD and estimate token amount
            liquidity_usd = pair_data.get('liquidity', {}).get('usd', 0)
            price_usd = float(pair_data.get('priceUsd', 0))
            
            if price_usd > 0:
                # Rough estimation of tokens in pool based on liquidity
                # This is an approximation since we don't have exact reserve data
                estimated_tokens = (liquidity_usd / 2) / price_usd
                return estimated_tokens
            
            return 0.0
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating token balance: {e}")
            return 0.0
    
    async def check_for_new_buys(self):
        """Check for new buy transactions."""
        try:
            current_data = await self.fetch_token_data()
            if not current_data or not current_data.get('pairs'):
                return
            
            pair = current_data['pairs'][0]  # Main trading pair
            txns = pair.get('txns', {})
            
            # Check for new buys in 5-minute window
            current_m5_buys = txns.get('m5', {}).get('buys', 0)
            current_h24_buys = txns.get('h24', {}).get('buys', 0)
            
            # Detect new buys
            new_m5_buys = current_m5_buys - self.last_m5_buys
            
            if new_m5_buys > 0:
                # Get current token stats
                token_balance = self.get_token_balance_from_pair(pair)
                price_usd = float(pair.get('priceUsd', 0))
                volume_m5 = pair.get('volume', {}).get('m5', 0)
                
                # Estimate buy amount from volume increase
                buy_amount_usd = volume_m5 / (current_m5_buys if current_m5_buys > 0 else 1)
                buy_amount_tokens = buy_amount_usd / price_usd if price_usd > 0 else 0
                
                # Calculate price change as impact indicator
                price_change_m5 = pair.get('priceChange', {}).get('m5', 0)
                
                logger.info(f"New buys detected: {new_m5_buys} buys, Est. amount: {buy_amount_tokens:.2f} tokens")
                
                # Trigger notification
                await self.notification_callback(
                    roar_tokens_left=token_balance,
                    buy_amount=buy_amount_tokens,
                    price_impact=abs(price_change_m5)
                )
            
            # Update tracking counters
            self.last_m5_buys = current_m5_buys
            self.last_h24_buys = current_h24_buys
            self.current_data = current_data
            
        except Exception as e:
            logger.error(f"Error checking for new buys: {e}")
    
    async def start_monitoring(self):
        """Start monitoring the token for new buys."""
        if not await self.initialize():
            logger.error("Failed to initialize monitor")
            return
        
        self.monitoring = True
        logger.info("Started DexScreener monitoring for Roaring Kitty token")
        
        while self.monitoring:
            try:
                await self.check_for_new_buys()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.monitoring = False
        logger.info("Stopped DexScreener monitoring")
    
    async def get_current_stats(self) -> Dict:
        """Get current token statistics."""
        try:
            if not self.current_data:
                self.current_data = await self.fetch_token_data()
            
            if not self.current_data or not self.current_data.get('pairs'):
                return {}
            
            pair = self.current_data['pairs'][0]
            token_balance = self.get_token_balance_from_pair(pair)
            
            return {
                'roar_tokens_left': token_balance,
                'price_usd': pair.get('priceUsd', 0),
                'volume_24h': pair.get('volume', {}).get('h24', 0),
                'buys_24h': pair.get('txns', {}).get('h24', {}).get('buys', 0),
                'sells_24h': pair.get('txns', {}).get('h24', {}).get('sells', 0),
                'liquidity_usd': pair.get('liquidity', {}).get('usd', 0),
                'market_cap': pair.get('marketCap', 0),
                'price_change_24h': pair.get('priceChange', {}).get('h24', 0),
                'pair_address': pair.get('pairAddress', 'N/A'),
                'dex_name': pair.get('dexId', 'Unknown'),
                'status': 'monitoring' if self.monitoring else 'stopped'
            }
            
        except Exception as e:
            logger.error(f"Error getting current stats: {e}")
            return {}