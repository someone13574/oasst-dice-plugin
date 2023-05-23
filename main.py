import json
import os
import random
from typing import Annotated
from fastapi import FastAPI, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/roll-dice", operation_id="rollDice", summary="Rolls dice based on the string in dice notation")
async def test_function(dice_to_roll: Annotated[str, Query(description="Dice shorthand of dice to roll (for example '2d8 + 6')")]) -> Response:
    try:
        # Splitting the string into components
        parts = dice_to_roll.split("d")
        num_dice = int(parts[0])
        dice_type, modifier = parts[1].split("+")
        dice_type = int(dice_type.strip())
        modifier = int(modifier.strip())

        # Rolling the dice
        dice_rolls = [random.randint(1, dice_type) for _ in range(num_dice)]

        # Calculating the sum of dice rolls and adding the modifier
        result = sum(dice_rolls) + modifier
        return Response(content=f"Result of roll {dice_to_roll=}: {result=}")

    except Exception as err:
        print(err)
        return JSONResponse(content={"error": err}, status_code=500)


@app.get("/icon.png", include_in_schema=False)
async def api_icon():
    with open("icon.png", "rb") as f:
        icon = f.read()
    return Response(content=icon, media_type="image/png")


@app.get("/ai-plugin.json", include_in_schema=False)
async def api_ai_plugin():
    with open("ai-plugin.json", "r") as f:
        ai_plugin_json = json.load(f)
    ai_plugin_json_str = json.dumps(ai_plugin_json).replace(
        "${PLUGIN_URL}", f"https://{os.getenv('VERCEL_GIT_REPO_SLUG')}-{os.getenv('VERCEL_GIT_REPO_OWNER')}.vercel.app")
    return Response(content=ai_plugin_json_str, media_type="application/json")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    # Load plugin information from ai-plugin.json file
    with open("ai-plugin.json", "r") as file:
        plugin_info = json.load(file)

    # Define the servers and tags for the OpenAPI scheme
    servers = [
        {"url": f"https://{os.getenv('VERCEL_GIT_REPO_SLUG')}-{os.getenv('VERCEL_GIT_REPO_OWNER')}.vercel.app"}]
    tags = [{"name": os.getenv('VERCEL_GIT_REPO_SLUG'), "description": ""}]

    # Generate the OpenAPI schema using the FastAPI utility function
    openapi_schema = get_openapi(
        title=plugin_info["name_for_human"],
        version="0.1",
        routes=app.routes,
        tags=tags,
        servers=servers,
    )

    openapi_schema.pop("components", None)
    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi
