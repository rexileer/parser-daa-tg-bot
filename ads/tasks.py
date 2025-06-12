import asyncio
import json
import redis.asyncio as aioredis
from django.db import close_old_connections
from asgiref.sync import sync_to_async
import logging
from datetime import datetime, timedelta

from .models import Advertisement
from config import REDIS_HOST, REDIS_PORT

logger = logging.getLogger(__name__)

async def save_ads_from_redis_to_db():
    """
    Save all advertisements from Redis to the database before they expire
    """
    redis_client = await aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    
    try:
        # Get all keys from Redis
        ad_keys = await redis_client.keys("*")
        
        if not ad_keys:
            logger.info("No ads found in Redis")
            return
            
        logger.info(f"Found {len(ad_keys)} ads in Redis")
        
        for ad_id in ad_keys:
            key_type = await redis_client.type(ad_id)
            
            # Skip non-string keys and special keys
            if key_type != "string" or ad_id.startswith("ads:"):
                continue
                
            ad_data = await redis_client.get(ad_id)
            
            if ad_data:
                try:
                    ad_dict = json.loads(ad_data)
                    
                    # Save to database
                    await sync_to_async(Advertisement.from_redis_data)(ad_id, ad_dict)
                    
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode JSON for ad {ad_id}")
                except Exception as e:
                    logger.error(f"Error saving ad {ad_id} to database: {e}")
    
    except Exception as e:
        logger.error(f"Error in save_ads_from_redis_to_db task: {e}")
    finally:
        await redis_client.close()
        close_old_connections()
        
async def cleanup_old_ads(days=1):
    """
    Clean up ads that are older than the specified number of days
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    try:
        # Delete old ads
        await sync_to_async(Advertisement.objects.filter)(created_at__lt=cutoff_date).delete()
        logger.info(f"Deleted ads older than {days} days")
    except Exception as e:
        logger.error(f"Error in cleanup_old_ads task: {e}")
    finally:
        close_old_connections()

async def run_periodic_tasks():
    """
    Run the tasks periodically
    """
    while True:
        try:
            # Save ads from Redis to database
            await save_ads_from_redis_to_db()
            
            # Clean up old ads (keep ads for 24 hours)
            await cleanup_old_ads(days=1)
            
            # Wait for 5 minutes before running again
            logger.info("Waiting 5 minutes before next run")
            await asyncio.sleep(300)
        except Exception as e:
            logger.error(f"Error in run_periodic_tasks: {e}")
            await asyncio.sleep(60)  # Wait a minute if there's an error 