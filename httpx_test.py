import os
import httpx
import asyncio
import dotenv
import time

dotenv.load_dotenv(".secrets")
URL = os.getenv("ICALDAV_URL")

async def fetch(url, method="get", headers=None, params=None, data=None, json=None):
    async with httpx.AsyncClient() as client:
        print(f"Fetching {url} with method {method.upper()}...")
        # Select the method dynamically
        response = await client.request(
            method.upper(),
            url,
            headers=headers,
            params=params,
            data=data if method.lower() != "get" else None,
            json=json if method.lower() != "get" else None,
            follow_redirects=True
        )
        print(f"Received response from {url} with status code {response.status_code}")
        return response

def main():
    url = URL
    loop = asyncio.get_event_loop()
    xml_body = """
    <?xml version="1.0" encoding="UTF-8"?>
    <C:calendar-query xmlns:D="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav">
     <D:prop>
       <D:getetag/>
       <C:calendar-data>
         <C:comp name="VCALENDAR">
           <C:prop name="VERSION"/>
           <C:comp name="VEVENT">
             <C:prop name="SUMMARY"/>
             <C:prop name="UID"/>
             <C:prop name="DTSTART"/>
             <C:prop name="DTEND"/>
             <C:prop name="DURATION"/>
             <C:prop name="RRULE"/>
             <C:prop name="RDATE"/>
             <C:prop name="EXRULE"/>
             <C:prop name="EXDATE"/>
             <C:prop name="RECURRENCE-ID"/>
           </C:comp>
           <C:comp name="VTIMEZONE"/>
         </C:comp>
       </C:calendar-data>
     </D:prop>
     <C:filter>
       <C:comp-filter name="VCALENDAR">
         <C:comp-filter name="VEVENT">
           <C:time-range start="20250101T000000Z"
                         end="20251231T000000Z"/>
         </C:comp-filter>
       </C:comp-filter>
     </C:filter>
   </C:calendar-query>

    """
    headers = {
        "Content-Type": "application/xml",
        "Depth": "1",
        "Accept": "application/xml"
    }
    task = loop.create_task(fetch(url, method="report", headers=headers, data=xml_body))
    while not task.done():
        print("Polling for response...")
        loop.run_until_complete(asyncio.sleep(0.1))
        time.sleep(0.1)
    response = task.result()
    print("Status code:", response.status_code)
    print("Response text:", response.text)
    print("Response headers:", response.headers)
    print("Response reason:", response.reason_phrase)

if __name__ == "__main__":
    main()