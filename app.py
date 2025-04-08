from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import requests
import json
from enum import Enum

# Load environment variables
load_dotenv()

app = FastAPI(title="Metal Prices API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
SPREADSHEET_ID = "1oUpFZQ6AgWb6Ssd5riWgYaxKXYUwRKqOWg0OXacf9NI"
MCP_URL = "https://mcp.composio.dev/googlesheets/uneven-tasteless-intern-TuxEbI"

class MetalCategory(str, Enum):
    FERROUS = "Ferrous Metals"
    COPPER = "Copper"
    BRASS = "Brass"
    ALUMINUM = "Aluminum"
    STAINLESS = "Stainless Steel"
    MISCELLANEOUS = "Miscellaneous"

def fetch_metal_prices() -> List[Dict]:
    """Fetch all metal prices from the Google Sheet"""
    try:
        # Make request to MCP server
        response = requests.post(
            f"{MCP_URL}/GOOGLESHEETS_BATCH_GET",
            json={
                "params": {
                    "spreadsheet_id": SPREADSHEET_ID
                }
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch data from Google Sheets")
        
        data = response.json()
        if not data.get("data") or not data["data"].get("spreadsheet_data"):
            raise HTTPException(status_code=500, detail="Invalid data format received")
        
        # Extract values from the response
        values = data["data"]["spreadsheet_data"]["valueRanges"]["values"]
        
        # Skip header row and convert to list of dictionaries
        metal_prices = []
        for row in values[1:]:  # Skip header row
            if len(row) >= 4:
                metal_prices.append({
                    "category": row[0],
                    "commodity": row[1],
                    "price": row[2],
                    "unit": row[3]
                })
        
        return metal_prices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the Metal Prices API"}

@app.get("/prices")
def get_all_prices():
    """Get all metal prices"""
    return fetch_metal_prices()

@app.get("/prices/{category}")
def get_prices_by_category(category: MetalCategory):
    """Get metal prices filtered by category"""
    all_prices = fetch_metal_prices()
    category_prices = [price for price in all_prices if price["category"] == category]
    if not category_prices:
        raise HTTPException(status_code=404, detail=f"No prices found for category: {category}")
    return category_prices

@app.get("/commodity/{commodity_name}")
def get_price_by_commodity(commodity_name: str):
    """Get price for a specific commodity"""
    all_prices = fetch_metal_prices()
    commodity_prices = [price for price in all_prices if price["commodity"].lower() == commodity_name.lower()]
    if not commodity_prices:
        raise HTTPException(status_code=404, detail=f"No price found for commodity: {commodity_name}")
    return commodity_prices[0]
