import feedparser
import aiohttp
from bs4 import BeautifulSoup
from typing import List
from models.incident import Incident


class AtomAdapter:
    def __init__(self, provider_name: str, feed_url: str):
        self.provider_name = provider_name
        self.feed_url = feed_url

    async def fetch_incidents(self) -> List[Incident]:
        raw_xml = await self._fetch_raw_feed()
        if raw_xml is None:
            return []
        return self._parse_feed(raw_xml)

    async def _fetch_raw_feed(self) -> str | None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.feed_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        print(f"[{self.provider_name}] Failed to fetch feed. HTTP {response.status}")
                        return None
        except Exception as e:
            print(f"[{self.provider_name}] Error fetching feed: {e}")
            return None

    def _parse_feed(self, raw_xml: str) -> List[Incident]:
        feed = feedparser.parse(raw_xml)
        incidents = []

        for entry in feed.entries:
            try:
                incident = self._parse_entry(entry)
                incidents.append(incident)
            except Exception as e:
                print(f"[{self.provider_name}] Error parsing entry: {e}")
                continue

        return incidents

    def _parse_entry(self, entry) -> Incident:
        incident_id = self._extract_id(entry.get("id", ""))
        title = self._clean_html(entry.get("title", "No title"))
        updated_at = entry.get("updated", "")
        incident_url = entry.get("link", "")
        content_html = entry.get("content", [{}])[0].get("value", "") or entry.get("summary", "")

        status = self._extract_status(content_html)
        affected_services = self._extract_services(content_html)
        latest_message = self._extract_message(content_html)

        return Incident(
            incident_id=incident_id,
            title=title,
            status=status,
            affected_services=affected_services,
            latest_message=latest_message,
            updated_at=updated_at,
            source_provider=self.provider_name,
            incident_url=incident_url,
        )

    def _extract_id(self, raw_id: str) -> str:
        # ID looks like: https://status.openai.com//incidents/01KHYH2KT8VNWS146V0S09MF29
        # We just want the last segment: 01KHYH2KT8VNWS146V0S09MF29
        return raw_id.rstrip("/").split("/")[-1]

    def _extract_status(self, content_html: str) -> str:
        soup = BeautifulSoup(content_html, "html.parser")
        bold_tag = soup.find("b")
        if bold_tag and "Status:" in bold_tag.text:
            return bold_tag.text.replace("Status:", "").strip()
        return "Unknown"

    def _extract_services(self, content_html: str) -> List[str]:
        soup = BeautifulSoup(content_html, "html.parser")
        services = []
        for li in soup.find_all("li"):
            # Each li looks like: "Conversations (Operational)"
            # Strip the state in brackets, keep just the service name
            service_text = li.text.strip()
            service_name = service_text.split("(")[0].strip()
            if service_name:
                services.append(service_name)
        return services

    def _extract_message(self, content_html: str) -> str:
        soup = BeautifulSoup(content_html, "html.parser")
        # Remove the <b>Status: ...</b> tag
        bold_tag = soup.find("b")
        if bold_tag:
            bold_tag.decompose()
        # Remove the <ul> services list
        ul_tag = soup.find("ul")
        if ul_tag:
            ul_tag.decompose()
        # Whatever plain text remains is the message
        message = soup.get_text(separator=" ").strip()
        return message if message else "No message available"

    def _clean_html(self, text: str) -> str:
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text().strip()