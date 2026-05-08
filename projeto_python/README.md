# Desafio Técnico - API de Foco e Produtividade

Backend em Python para registrar blocos de foco e gerar diagnóstico de produtividade com feedback automático.

## Stack

- Python 3.12+
- FastAPI
- Armazenamento em memória (lista de registros)
- Testes com `pytest`

## Como rodar

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Inicie o servidor:

```bash
python -m uvicorn app.main:app --reload
```

3. Acesse a documentação automática:

- Interface web (padrão): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Interface web alternativa: [http://127.0.0.1:8000/interface](http://127.0.0.1:8000/interface)
- Swagger UI: [http://127.0.0.1:8000/swagger](http://127.0.0.1:8000/swagger)

## Endpoints

### `POST /registro-foco`

Registra um bloco de trabalho encerrado.

Campos esperados:

- `nivel_foco`: inteiro de 1 a 5 (obrigatório)
- `tempo_minutos`: inteiro > 0 (obrigatório)
- `comentario`: texto entre 3 e 500 caracteres (obrigatório)
- `categoria`: `coding`, `reuniao`, `estudo` ou `outros` (opcional)
- `tags`: lista de strings, até 10 itens (opcional)

Exemplo:

```json
{
  "nivel_foco": 5,
  "tempo_minutos": 60,
  "comentario": "Implementei autenticação da API.",
  "categoria": "coding",
  "tags": ["backend", "fastapi"]
}
```

### `GET /diagnostico-produtividade`

Retorna:

- média do nível de foco
- tempo total focado (minutos)
- total de registros
- categoria mais frequente
- feedback inteligente baseado no histórico

## Regras de feedback implementadas

- Média `< 3`: sugere pausas melhores e menos notificações
- Média entre `3` e `< 4`: foco estável com sugestão de meta por sessão
- Média `>= 4` e tempo total `>= 180`: maratona produtiva
- Média `>= 4` em outros cenários: foco ótimo

## Executar testes

```bash
python -m pytest -q
```

## Tratamento de erros

- `422 Unprocessable Entity` para payload inválido (ex.: `nivel_foco` fora de 1-5)
- `404 Not Found` em `GET /diagnostico-produtividade` quando não há registros

## Uso do Cursor (IA)

Este projeto foi desenvolvido com apoio do Cursor para acelerar tarefas de:

- estruturação inicial da API
- geração e ajuste de endpoints
- criação de testes automatizados
- melhoria da documentação e interface

Todo o conteúdo gerado com IA foi revisado, validado em execução local e adaptado manualmente antes da entrega.
