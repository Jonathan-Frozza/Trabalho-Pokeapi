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
