def format_pokemon_response(data):
    return {
        "name": data["name"],
        "id": data["id"],
        "height": data["height"],
        "weight": data["weight"],
        "types": [t["type"]["name"] for t in data["types"]],
        "sprites": {
            "front_default": data["sprites"]["front_default"],
            "back_default": data["sprites"]["back_default"]
        }
    }
