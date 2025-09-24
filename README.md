# Pokémon Proxy API

API em **FastAPI** que consome a [PokeAPI](https://pokeapi.co/) e adiciona recursos extras:

Paginação  
Cache com Redis  
Autenticação via API Key  
Rate limiting  
Docker + docker-compose  
Testes automatizados  

## Como rodar localmente

```bash
docker-compose up --build
```

API disponível em: [http://localhost:8000/docs](http://localhost:8000/docs)

## Testes

```bash
pytest 
```
##  Exemplo de requisição e resposta da API

### Listar Pokémons
**Request:**
```http
GET /pokemons?limit=2&offset=0
X-API-Key: 123

{
  "data": {
    "results": [
      { "name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/" },
      { "name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/" }
    ]
  }
}

GET /pokemons/25
X-API-Key: 123

{
  "data": {
    "id": 25,
    "name": "pikachu",
    "height": 4,
    "weight": 60,
    "types": [
      { "slot": 1, "type": { "name": "electric", "url": "https://pokeapi.co/api/v2/type/13/" } }
    ]
  }
}
