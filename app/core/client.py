"""
FIBO Client - Handles API communication with Bria FIBO for text-to-image generation.
"""
import os
import logging
import requests
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw
from io import BytesIO
from ..models import config

logger = logging.getLogger(__name__)


class FiboClient:
    """
    Client for the Bria FIBO API.
    
    Handles text-to-image generation with polling support for async responses.
    """

    def __init__(self):
        self.api_url = config.FIBO_API_URL
        self.api_key = config.FIBO_API_KEY
        
    def _create_placeholder_image(self, save_path: str, text: str = "FIBO OFFLINE") -> str:
        """
        Creates a placeholder image when API is unavailable or fails.
        """
        logger.warning(f"Creating placeholder image at {save_path} because API key/url is missing or error occurred.")
        
        # Create a simple gray image
        img = Image.new('RGB', (512, 512), color='gray')
        d = ImageDraw.Draw(img)
        
        # Draw text in the center
        # Note: Using default font since we can't guarantee system fonts
        d.text((200, 250), text, fill=(255, 255, 255))
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path)
        return save_path

    def _get_headers(self) -> Dict[str, str]:
        """
        Constructs headers expecting 'api_token' as per FAL FIBO curl examples.
        """
        return {
            "api_token": self.api_key if self.api_key else "",
            "Content-Type": "application/json"
        }

    def _save_image_from_url(self, image_url: str, save_path: str) -> None:
        """
        Downloads and saves an image from a URL.
        """
        response = requests.get(image_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        image.save(save_path)

    def _extract_image_url(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Robustly extracts image URL from API response.
        Handles both direct 'images' array and nested 'result.image_url' format from Bria.
        """
        # Check for nested result.image_url (Bria async response format)
        if "result" in data and isinstance(data["result"], dict):
            if "image_url" in data["result"]:
                return data["result"]["image_url"]
        
        # Check for direct image_url
        if "image_url" in data:
            return data["image_url"]
        
        # Check for images array
        if "images" in data and isinstance(data["images"], list) and len(data["images"]) > 0:
            first = data["images"][0]
            if isinstance(first, dict) and "url" in first:
                return first["url"]
            elif isinstance(first, str):
                return first
        return None

    def _poll_for_result(self, status_url: str, max_attempts: int = 30, delay: float = 1.0) -> Dict[str, Any]:
        """
        Polls the status_url until the image is ready or max attempts reached.
        """
        import time
        for attempt in range(max_attempts):
            logger.info(f"Polling status (attempt {attempt+1}/{max_attempts}): {status_url}")
            response = requests.get(status_url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status", "").lower()
            
            # Check if we already have an image URL regardless of status
            image_url = self._extract_image_url(data)
            if image_url:
                logger.info(f"Found image URL in polling response")
                return data
            
            # Check various success statuses
            if status in ["completed", "succeeded", "ready", "done", "success", "finished"]:
                return data
            elif status in ["failed", "error"]:
                raise ValueError(f"API generation failed: {data}")
            elif status in ["processing", "pending", "in_progress", "queued"]:
                # Still processing, continue polling
                time.sleep(delay)
            else:
                # Unknown status, log it and continue
                logger.warning(f"Unknown status: {status}, continuing to poll...")
                time.sleep(delay)
        
        raise TimeoutError(f"Polling timed out after {max_attempts} attempts")

    def generate_image(self, payload: Dict[str, Any], project_id: str, shot_id: str) -> Dict[str, Any]:
        """
        Generates an image from text (Text2Img).
        
        Args:
            payload: JSON payload for the API (must include 'prompt').
            project_id: ID of the project folder.
            shot_id: ID of the shot.
            
        Returns:
            Dict containing metadata and result path.
        """
        target_path = os.path.join(config.OUTPUT_DIR, project_id, f"shot_{shot_id}.png")
        
        # Check Offline/Missing Config
        if not self.api_key or not self.api_url:
            self._create_placeholder_image(target_path, "NO API KEY/URL")
            return {
                "image_path": target_path,
                "project_id": project_id,
                "shot_id": shot_id,
                "mode": "text2img",
                "status": "offline_placeholder"
            }

        try:
            logger.info(f"Sending request to {self.api_url} for shot {shot_id}")
            
            # Build API payload with FIBO parameters
            api_payload = {
                "prompt": payload.get("prompt", "")
            }
            
            # Add negative_prompt if provided
            neg = payload.get("negative_prompt", "")
            if neg:
                api_payload["negative_prompt"] = neg
            
            # FIBO Inspire Mode: Add image_url for reference-based generation
            image_url = payload.get("image_url")
            if image_url:
                api_payload["image_url"] = image_url
                logger.info(f"Using Inspire Mode with reference image: {image_url[:50]}...")
            
            # Add optional FIBO-specific parameters if provided
            if "aspect_ratio" in payload:
                api_payload["aspect_ratio"] = payload["aspect_ratio"]
            if "num_images" in payload:
                api_payload["num_images"] = payload["num_images"]
            
            response = requests.post(
                self.api_url, 
                json=api_payload, 
                headers=self._get_headers(), 
                timeout=60
            )
            
            if not response.ok:
                logger.error(f"API error ({response.status_code}): {response.text}")
            response.raise_for_status()
            data = response.json()
            
            # Handle async response - poll if status_url is returned
            image_url = self._extract_image_url(data)
            final_response = data
            
            if not image_url and "status_url" in data:
                logger.info(f"Async response detected, polling status_url...")
                final_response = self._poll_for_result(data["status_url"])
                image_url = self._extract_image_url(final_response)
            
            if not image_url:
                raise ValueError(f"No image URL found in response: {final_response}")

            self._save_image_from_url(image_url, target_path)

            return {
                "image_path": target_path,
                "project_id": project_id,
                "shot_id": shot_id,
                "mode": "text2img",
                "status": "success"
            }

        except Exception as e:
            error_str = str(e)
            logger.error(f"Error generating image: {error_str}")
            
            # Translate technical errors to user-friendly messages
            user_message = error_str
            if "401" in error_str or "Unauthorized" in error_str:
                user_message = "API key invalid or expired. Please check your FIBO_API_KEY."
            elif "422" in error_str or "Unprocessable" in error_str:
                user_message = "Invalid request format. The prompt may contain unsupported content."
            elif "429" in error_str or "Too Many" in error_str:
                user_message = "Rate limit exceeded. Please wait a moment and try again."
            elif "500" in error_str or "Internal Server" in error_str:
                user_message = "API server error. Please try again later."
            elif "timeout" in error_str.lower():
                user_message = "Request timed out. The server may be busy."
            
            self._create_placeholder_image(target_path, "ERROR")
            return {
                "image_path": target_path,
                "project_id": project_id,
                "shot_id": shot_id,
                "mode": "text2img",
                "status": "error",
                "error": user_message,
                "technical_error": error_str
            }

    # =========================================================================
    # PRO FEATURES - Bria API V2 Image Editing
    # =========================================================================
    
    def remove_background(self, image_path: str, output_path: str) -> Dict[str, Any]:
        """
        Removes background from an image using Bria RMBG 2.0.
        """
        if not self.api_key:
            return {"status": "error", "error": "API key not configured"}
        
        try:
            import base64
            with open(image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            
            api_url = "https://engine.prod.bria-api.com/v1/background/remove"
            response = requests.post(
                api_url,
                json={"image": f"data:image/png;base64,{img_data}"},
                headers=self._get_headers(),
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            # Handle async response
            if "status_url" in data:
                data = self._poll_for_result(data["status_url"])
            
            image_url = self._extract_image_url(data) or data.get("result_url")
            if image_url:
                self._save_image_from_url(image_url, output_path)
                return {"status": "success", "image_path": output_path}
            
            return {"status": "error", "error": "No result image returned"}
            
        except Exception as e:
            logger.error(f"Background removal failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def generative_fill(self, image_path: str, mask_path: str, prompt: str, output_path: str) -> Dict[str, Any]:
        """
        Fills masked areas with AI-generated content (inpainting).
        """
        if not self.api_key:
            return {"status": "error", "error": "API key not configured"}
        
        try:
            import base64
            with open(image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            with open(mask_path, "rb") as f:
                mask_data = base64.b64encode(f.read()).decode()
            
            api_url = "https://engine.prod.bria-api.com/v1/eraser/replace"
            response = requests.post(
                api_url,
                json={
                    "image": f"data:image/png;base64,{img_data}",
                    "mask": f"data:image/png;base64,{mask_data}",
                    "prompt": prompt
                },
                headers=self._get_headers(),
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            if "status_url" in data:
                data = self._poll_for_result(data["status_url"])
            
            image_url = self._extract_image_url(data) or data.get("result_url")
            if image_url:
                self._save_image_from_url(image_url, output_path)
                return {"status": "success", "image_path": output_path}
            
            return {"status": "error", "error": "No result image returned"}
            
        except Exception as e:
            logger.error(f"Generative fill failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def erase_object(self, image_path: str, mask_path: str, output_path: str) -> Dict[str, Any]:
        """
        Erases objects from image and fills intelligently.
        """
        if not self.api_key:
            return {"status": "error", "error": "API key not configured"}
        
        try:
            import base64
            with open(image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            with open(mask_path, "rb") as f:
                mask_data = base64.b64encode(f.read()).decode()
            
            api_url = "https://engine.prod.bria-api.com/v1/eraser"
            response = requests.post(
                api_url,
                json={
                    "image": f"data:image/png;base64,{img_data}",
                    "mask": f"data:image/png;base64,{mask_data}"
                },
                headers=self._get_headers(),
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            if "status_url" in data:
                data = self._poll_for_result(data["status_url"])
            
            image_url = self._extract_image_url(data) or data.get("result_url")
            if image_url:
                self._save_image_from_url(image_url, output_path)
                return {"status": "success", "image_path": output_path}
            
            return {"status": "error", "error": "No result image returned"}
            
        except Exception as e:
            logger.error(f"Eraser failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def expand_image(self, image_path: str, output_path: str, aspect_ratio: str = "16:9") -> Dict[str, Any]:
        """
        Expands image beyond its borders (outpainting).
        """
        if not self.api_key:
            return {"status": "error", "error": "API key not configured"}
        
        try:
            import base64
            with open(image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            
            api_url = "https://engine.prod.bria-api.com/v1/image/expand"
            response = requests.post(
                api_url,
                json={
                    "image": f"data:image/png;base64,{img_data}",
                    "aspect_ratio": aspect_ratio
                },
                headers=self._get_headers(),
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            if "status_url" in data:
                data = self._poll_for_result(data["status_url"])
            
            image_url = self._extract_image_url(data) or data.get("result_url")
            if image_url:
                self._save_image_from_url(image_url, output_path)
                return {"status": "success", "image_path": output_path}
            
            return {"status": "error", "error": "No result image returned"}
            
        except Exception as e:
            logger.error(f"Expand failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def enhance_image(self, image_path: str, output_path: str) -> Dict[str, Any]:
        """
        Enhances and upscales image quality.
        """
        if not self.api_key:
            return {"status": "error", "error": "API key not configured"}
        
        try:
            import base64
            with open(image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()
            
            api_url = "https://engine.prod.bria-api.com/v1/image/enhance"
            response = requests.post(
                api_url,
                json={"image": f"data:image/png;base64,{img_data}"},
                headers=self._get_headers(),
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            if "status_url" in data:
                data = self._poll_for_result(data["status_url"])
            
            image_url = self._extract_image_url(data) or data.get("result_url")
            if image_url:
                self._save_image_from_url(image_url, output_path)
                return {"status": "success", "image_path": output_path}
            
            return {"status": "error", "error": "No result image returned"}
            
        except Exception as e:
            logger.error(f"Enhance failed: {e}")
            return {"status": "error", "error": str(e)}
