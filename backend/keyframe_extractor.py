import os
import json
import subprocess
from typing import List, Dict, Tuple
from pathlib import Path

class KeyFrameExtractor:
    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe"):
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path
    
    def extract_keyframes(self, video_path: str, output_dir: str) -> Dict:
        """
        Extract key frames from video and return metadata
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get video filename without extension
        video_name = Path(video_path).stem
        
        # Extract key frames using FFmpeg
        frames_output = os.path.join(output_dir, f"{video_name}-keyframe-%03d-%09d.png")
        
        ffmpeg_cmd = [
            self.ffmpeg_path,
            "-i", video_path,
            "-vf", "select=eq(pict_type\\,PICT_TYPE_I)",
            "-vsync", "2",
            "-frame_pts", "1",
            "-y",  # Overwrite output files
            frames_output
        ]
        
        try:
            # Run FFmpeg command
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get key frame timestamps using FFprobe
            timestamps = self._get_keyframe_timestamps(video_path)
            
            # Get list of generated frame files
            frame_files = self._get_frame_files(output_dir, video_name)
            
            return {
                "success": True,
                "frames_extracted": len(frame_files),
                "frame_files": frame_files,
                "timestamps": timestamps,
                "output_directory": output_dir
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"FFmpeg error: {e.stderr}",
                "frames_extracted": 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "frames_extracted": 0
            }
    
    def _get_keyframe_timestamps(self, video_path: str) -> List[Dict]:
        """
        Extract key frame timestamps using FFprobe
        """
        ffprobe_cmd = [
            self.ffprobe_path,
            "-v", "quiet",
            "-select_streams", "v:0",
            "-show_entries", "frame=pict_type,pts_time",
            "-of", "json",
            video_path
        ]
        
        try:
            result = subprocess.run(
                ffprobe_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            data = json.loads(result.stdout)
            keyframes = []
            
            for frame in data.get("frames", []):
                if frame.get("pict_type") == "I":
                    keyframes.append({
                        "timestamp": float(frame.get("pts_time", 0)),
                        "pts_time": frame.get("pts_time", "0"),
                        "description": f"Key frame at {frame.get('pts_time', '0')} seconds"
                    })
            
            return keyframes
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            return []
    
    def _get_frame_files(self, output_dir: str, video_name: str) -> List[str]:
        """
        Get list of generated frame files
        """
        frame_files = []
        for file in os.listdir(output_dir):
            if file.startswith(f"{video_name}-keyframe-") and file.endswith(".png"):
                frame_files.append(file)
        
        return sorted(frame_files) 