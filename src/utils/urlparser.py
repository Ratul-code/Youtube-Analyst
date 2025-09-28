from urllib.parse import urlparse, parse_qs

def get_youtube_video_id(url: str) -> str | None:

    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname or ""
        
        if "youtu.be" in hostname:
            # Example: https://youtu.be/Ey18PDiaAYI
            return parsed_url.path.lstrip("/")
        
        if "youtube.com" in hostname:
            if parsed_url.path == "/watch":
                # Example: https://www.youtube.com/watch?v=Ey18PDiaAYI
                query = parse_qs(parsed_url.query)
                return query.get("v", [None])[0]
            elif parsed_url.path.startswith("/embed/"):
                # Example: https://www.youtube.com/embed/Ey18PDiaAYI
                return parsed_url.path.split("/")[2]
            elif parsed_url.path.startswith("/v/"):
                # Example: https://www.youtube.com/v/Ey18PDiaAYI
                return parsed_url.path.split("/")[2]
        
        return None  # Not a recognized YouTube URL
    except Exception:
        return None
