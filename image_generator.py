"""
Image generator for Uniswap pool notifications.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import io

class NotificationImageGenerator:
    def __init__(self, background_image_path):
        """Initialize the image generator with background image."""
        self.background_path = background_image_path
        self.font_size_large = 48
        self.font_size_medium = 36
        self.font_size_small = 24
        
    def create_notification_image(self, roar_tokens_left, buy_amount=None, price_impact=None):
        """
        Create a notification image with ROAR token information.
        
        Args:
            roar_tokens_left (float): Number of ROAR tokens remaining in pool
            buy_amount (float, optional): Amount of tokens bought
            price_impact (float, optional): Price impact percentage
            
        Returns:
            io.BytesIO: Image data as bytes
        """
        # Load background image
        try:
            background = Image.open(self.background_path)
        except Exception as e:
            # Create a default background if image loading fails
            background = Image.new('RGB', (800, 600), color='#1a1a2e')
        
        # Ensure image is in RGBA mode for transparency support
        if background.mode != 'RGBA':
            background = background.convert('RGBA')
        
        # Create a copy to work with
        img = background.copy()
        draw = ImageDraw.Draw(img)
        
        # Try to load custom fonts, fallback to default
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", self.font_size_large)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.font_size_medium)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", self.font_size_small)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Get image dimensions
        img_width, img_height = img.size
        
        # Create semi-transparent overlay for text readability
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 128))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Add overlay rectangle for text area
        text_area_height = 200
        text_y_start = img_height - text_area_height - 50
        overlay_draw.rectangle([50, text_y_start, img_width - 50, text_y_start + text_area_height], 
                              fill=(0, 0, 0, 180))
        
        # Composite overlay with main image
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)
        
        # Format the ROAR tokens left number
        if roar_tokens_left >= 1000000:
            roar_display = f"{roar_tokens_left/1000000:.2f}M"
        elif roar_tokens_left >= 1000:
            roar_display = f"{roar_tokens_left/1000:.2f}K"
        else:
            roar_display = f"{roar_tokens_left:.2f}"
        
        # Main text: Number of ROAR Left
        main_text = f"ROAR LEFT: {roar_display}"
        
        # Calculate text position for centering
        bbox = draw.textbbox((0, 0), main_text, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_x = (img_width - text_width) // 2
        text_y = text_y_start + 30
        
        # Draw main text with outline for better visibility
        outline_color = (0, 0, 0, 255)
        text_color = (238, 238, 238, 255)  # Light text color
        
        # Draw text outline
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    draw.text((text_x + dx, text_y + dy), main_text, font=font_large, fill=outline_color)
        
        # Draw main text
        draw.text((text_x, text_y), main_text, font=font_large, fill=text_color)
        
        # Add additional info if provided
        if buy_amount is not None:
            buy_text = f"Buy: {buy_amount:.4f} ROAR"
            bbox = draw.textbbox((0, 0), buy_text, font=font_medium)
            text_width = bbox[2] - bbox[0]
            text_x = (img_width - text_width) // 2
            text_y += 60
            
            # Draw with outline
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        draw.text((text_x + dx, text_y + dy), buy_text, font=font_medium, fill=outline_color)
            draw.text((text_x, text_y), buy_text, font=font_medium, fill=text_color)
        
        if price_impact is not None:
            impact_text = f"Price Impact: {price_impact:.2f}%"
            bbox = draw.textbbox((0, 0), impact_text, font=font_small)
            text_width = bbox[2] - bbox[0]
            text_x = (img_width - text_width) // 2
            text_y += 40
            
            # Color code price impact
            impact_color = (255, 100, 100, 255) if price_impact > 5 else (100, 255, 100, 255)
            
            # Draw with outline
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        draw.text((text_x + dx, text_y + dy), impact_text, font=font_small, fill=outline_color)
            draw.text((text_x, text_y), impact_text, font=font_small, fill=impact_color)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr