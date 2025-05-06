import aiohttp

async def call_sandbox_microservice(url: str) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("http://sandbox:8000/analyze", json={"url": url}) as resp:
                return await resp.json()
    except Exception as e:
        return {"error": f"Sandbox connection failed: {str(e)}"}

