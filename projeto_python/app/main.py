from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import Body, FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field


tags_metadata = [
    {
        "name": "Interface",
        "description": "Tela simples para preencher os dados da API no navegador.",
    },
    {
        "name": "Registros",
        "description": "Cadastro de sessões de foco finalizadas.",
    },
    {
        "name": "Diagnóstico",
        "description": "Resumo inteligente da produtividade com base no histórico.",
    },
]

app = FastAPI(
    title="API de Foco e Produtividade",
    description=(
        "API para registrar blocos de trabalho e gerar um diagnóstico de produtividade.\n\n"
        "### Como usar\n"
        "1. Registre suas sessões em `POST /registro-foco`\n"
        "2. Consulte seu resumo em `GET /diagnostico-produtividade`\n\n"
        "### Autor(a)\n"
        "- Linkedin - Maria Fernanda Silva Lira\n"
        "- GitHub: https://github.com/maliraa07\n"
        "- LinkedIn: https://www.linkedin.com/in/mariafernandalira0702/"
    ),
    version="1.0.0",
    contact={
        "name": "Meu Portfólio",
        "url": "https://devmaliraa07.netlify.app/",
    },
    openapi_tags=tags_metadata,
    docs_url=None,
    redoc_url=None,
)


class RegistroFocoIn(BaseModel):
    nivel_foco: int = Field(ge=1, le=5, description="1 (distraído) até 5 (flow)")
    tempo_minutos: int = Field(gt=0, description="Duração da sessão em minutos")
    comentario: str = Field(min_length=3, max_length=500)
    categoria: Literal["coding", "reuniao", "estudo", "outros"] = "outros"
    tags: list[str] = Field(default_factory=list, max_length=10)


class RegistroFoco(RegistroFocoIn):
    id: int
    criado_em: datetime


class RegistroFocoResponse(BaseModel):
    mensagem: str
    registro: RegistroFoco


class DiagnosticoResponse(BaseModel):
    media_nivel_foco: float
    tempo_total_focado_minutos: int
    total_registros: int
    categoria_mais_frequente: str
    feedback: str


# Armazenamento simples em memória para o desafio.
registros: list[RegistroFoco] = []
ui_path = Path(__file__).with_name("ui.html")


@app.get(
    "/interface",
    tags=["Interface"],
    summary="Abrir interface web de preenchimento",
    description="Retorna uma tela HTML para registrar sessões e consultar diagnóstico.",
    include_in_schema=True,
)
def abrir_interface() -> FileResponse:
    return FileResponse(ui_path)


@app.get("/docs", include_in_schema=False)
def docs_com_interface() -> FileResponse:
    return FileResponse(ui_path)


@app.get("/swagger", include_in_schema=False)
def abrir_swagger():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
    )


@app.get("/", include_in_schema=False)
def raiz() -> FileResponse:
    return FileResponse(ui_path)


@app.post(
    "/registro-foco",
    status_code=201,
    response_model=RegistroFocoResponse,
    tags=["Registros"],
    summary="Registrar bloco de foco",
    description=(
        "Salva uma sessão recém-encerrada com nível de foco, duração e contexto.\n"
        "Use `categoria` e `tags` para enriquecer o diagnóstico."
    ),
)
def criar_registro(
    payload: RegistroFocoIn = Body(
        ...,
        examples=[
            {
                "nivel_foco": 5,
                "tempo_minutos": 75,
                "comentario": "Implementei endpoints e testes.",
                "categoria": "coding",
                "tags": ["backend", "fastapi"],
            }
        ],
    )
) -> RegistroFocoResponse:
    # Gera ID sequencial e timestamp UTC para rastreabilidade.
    novo_registro = RegistroFoco(
        id=len(registros) + 1,
        criado_em=datetime.now(timezone.utc),
        **payload.model_dump(),
    )
    registros.append(novo_registro)
    return RegistroFocoResponse(
        mensagem="Registro salvo com sucesso.",
        registro=novo_registro,
    )


def gerar_feedback(media_foco: float, total_minutos: int, total_registros: int) -> str:
    # Regras de negócio para transformar métricas em mensagem acionável.
    if total_registros == 0:
        return "Sem dados suficientes. Registre uma sessão para receber diagnóstico."
    if media_foco < 3:
        return (
            "Seu foco está abaixo do ideal. Tente blocos menores de trabalho, "
            "pausas mais longas e redução de notificações."
        )
    if media_foco < 4:
        return (
            "Seu foco está estável. Experimente definir uma meta específica por sessão "
            "para elevar a consistência."
        )
    if total_minutos >= 180:
        return "Você está em uma maratona produtiva de alto nível. Mantenha esse ritmo!"
    return "Ótimo nível de foco. Você está em um bom caminho de produtividade."


@app.get(
    "/diagnostico-produtividade",
    response_model=DiagnosticoResponse,
    tags=["Diagnóstico"],
    summary="Gerar diagnóstico de produtividade",
    description=(
        "Calcula média de foco, tempo total e categoria predominante para retornar "
        "um feedback automático e orientado por dados."
    ),
)
def diagnostico_produtividade() -> DiagnosticoResponse:
    if not registros:
        raise HTTPException(
            status_code=404,
            detail="Nenhum registro encontrado. Use POST /registro-foco primeiro.",
        )

    # Consolida os indicadores principais para o diagnóstico final.
    total_registros = len(registros)
    total_minutos = sum(registro.tempo_minutos for registro in registros)
    media_foco = sum(registro.nivel_foco for registro in registros) / total_registros

    # Conta frequência de categoria para indicar padrão de atividade.
    categorias: dict[str, int] = {}
    for registro in registros:
        categorias[registro.categoria] = categorias.get(registro.categoria, 0) + 1

    categoria_principal = max(categorias, key=categorias.get)
    feedback = gerar_feedback(media_foco, total_minutos, total_registros)

    return DiagnosticoResponse(
        media_nivel_foco=round(media_foco, 2),
        tempo_total_focado_minutos=total_minutos,
        total_registros=total_registros,
        categoria_mais_frequente=categoria_principal,
        feedback=feedback,
    )
