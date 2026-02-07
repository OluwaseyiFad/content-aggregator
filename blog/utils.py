import html
import requests
import re
from io import BytesIO
from PIL import Image
from dateutil import parser

from django.db.models import Q


CLEANR = re.compile('<.*?>')

def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext


def extract_images_from_html(html_content):
    """Extract image URLs from HTML content."""
    if not html_content:
        return []
    # Find all img src attributes
    img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
    return img_pattern.findall(html_content)


def validate_image_url(url, min_width=200):
    """Validate an image URL and return its width if valid."""
    try:
        response = requests.get(url, stream=True, timeout=5)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        width = img.size[0]
        if width >= min_width:
            return width
    except (requests.exceptions.RequestException, IOError, Image.DecompressionBombWarning):
        pass
    return 0


def find_content_image(item):
    """Find the best quality image from RSS feed item.

    Prioritizes full-size images over thumbnails and selects
    the largest available image when multiple options exist.
    Also extracts images from HTML content as fallback.
    """
    # Priority order: full-size images first, thumbnails last
    image_fields = ["media_content", "enclosures", "links", "media_group", "image", "media_thumbnail", "thumbnail"]

    best_image = None
    best_width = 0

    for field in image_fields:
        if not hasattr(item, field):
            continue

        value = getattr(item, field)
        if not value:
            continue

        # Handle list of media items
        if isinstance(value, list):
            for media_item in value:
                if not isinstance(media_item, dict):
                    continue

                url = media_item.get("url")
                if not url:
                    continue

                # Skip non-image content types
                media_type = media_item.get("type", "")
                if media_type and not media_type.startswith("image"):
                    continue

                # Get width if available, prefer larger images
                width = 0
                if "width" in media_item:
                    try:
                        width = int(media_item["width"])
                    except (ValueError, TypeError):
                        pass

                # If we have a width and it's larger, or no best yet
                if width > best_width or (best_image is None and width == 0):
                    actual_width = validate_image_url(url)
                    if actual_width > 0:
                        if width == 0:
                            width = actual_width
                        if width > best_width:
                            best_width = width
                            best_image = url
                        if best_width >= 400:
                            return best_image

        # Handle single dict value
        elif isinstance(value, dict) and "url" in value:
            url = value["url"]
            width = validate_image_url(url)
            if width > best_width:
                best_width = width
                best_image = url
            if best_width >= 400:
                return best_image

    # If no image found in media fields, try extracting from HTML content
    if not best_image:
        html_fields = ['content', 'summary', 'description']
        for field in html_fields:
            content = item.get(field, '')
            if isinstance(content, list) and content:
                content = content[0].get('value', '') if isinstance(content[0], dict) else str(content[0])

            if content:
                img_urls = extract_images_from_html(content)
                for url in img_urls[:3]:  # Check first 3 images only
                    # Skip tiny icons and tracking pixels
                    if any(skip in url.lower() for skip in ['icon', 'logo', 'badge', 'button', 'tracking', '1x1']):
                        continue
                    width = validate_image_url(url)
                    if width > best_width:
                        best_width = width
                        best_image = url
                    if best_width >= 400:
                        return best_image

    return best_image


def save_new_contents(feed, Content):
    """Saves new contents to the database.

    Checks the content GUID against the contents currently stored in the
    database. If not found, then a new `Content` is added to the database.

    Args:
        feed: requires a feedparser object
    """

    try:
        content_title = feed.channel.get('title', 'Technology')
    except AttributeError:
        content_title = "Technology"

    counter = 0
    for item in feed.entries:
        try:
            if counter >= 3:
                break
            guid = item.get('guid', item.get('id', ''))
            if not Content.objects.filter(Q(guid=guid) | Q(link=item.get('link', item.get('url', '')))).exists():
                content_image = find_content_image(item)
                tzinfos = {"PDT": -25200, "PST": -28800}  # PDT and PST offsets in seconds
                pub_date = parser.parse(item.get('published', item.get('updated', '')), tzinfos=tzinfos)
                description = html.unescape(cleanhtml(item.get('description', item.get('summary', ''))))
                title = html.unescape(cleanhtml(item.get('title', item.get('name', ''))))
                content = Content(
                    title=title,
                    description=description,
                    pub_date=pub_date,
                    link=item.get('link', item.get('url', '')),
                    content_name=content_title,
                    guid=guid,
                    image=content_image,
                )
                content.save()
                counter += 1
        except Exception as e:
            print(f"An error occurred while saving the contents for {content_title}: {e}")
