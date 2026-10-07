import os
import logging
import re
import json
import httpx

# Configuração controlada para ambientes locais/corporativos com certificados autoassinados
if os.getenv("DISABLE_SSL_VERIFY", "true").lower() in ("true", "1"):
    _orig_async_init = httpx.AsyncClient.__init__
    def _new_async_init(self, *args, **kwargs):
        kwargs['verify'] = False
        _orig_async_init(self, *args, **kwargs)
    httpx.AsyncClient.__init__ = _new_async_init

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage


def _listar_modelos_candidates():
    modelos = []
    for chave in ["GROK_MODEL", "GROQ_MODEL"]:
        configurado = os.getenv(chave)
        if configurado:
            modelos.append(configurado)
    modelos.extend([
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-120b",
        "grok-2-latest",
        "grok-3-mini",
    ])
    return list(dict.fromkeys(modelos))


def _resolve_provider_config(escola_id: int | None = None) -> dict:
    if escola_id is not None:
        from .store import get_school_credentials
        escola = get_school_credentials(escola_id)
        if escola and escola.get("api_key_ia"):
            provider = (escola.get("provedor_ia") or "grok").strip() or "grok"
            return {
                "provider": provider,
                "api_key": escola["api_key_ia"],
                "model": escola.get("modelo_ia") or ("grok-2-latest" if provider == "grok" else "openai/gpt-oss-20b"),
                "base_url": "https://api.x.ai/v1" if provider == "grok" else "https://api.groq.com/openai/v1",
            }

    grok_key = os.getenv("GROK_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    if grok_key:
        return {
            "provider": "grok",
            "api_key": grok_key,
            "model": os.getenv("GROK_MODEL", "grok-2-latest"),
            "base_url": os.getenv("GROK_BASE_URL", "https://api.x.ai/v1"),
        }
    if groq_key:
        return {
            "provider": "groq",
            "api_key": groq_key,
            "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            "base_url": os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        }
    return {"provider": "none", "api_key": None, "model": None, "base_url": None}


async def _chamada_llm_json(system_prompt: str, human_prompt: str, temperatura: float = 0.2, fallback_model: str | None = None, escola_id: int | None = None) -> str:
    provider_cfg = _resolve_provider_config(escola_id)
    provider = provider_cfg["provider"]

    if provider == "grok":
        headers = {"Authorization": f"Bearer {provider_cfg['api_key']}", "Content-Type": "application/json"}
        payload = {
            "model": provider_cfg["model"] or fallback_model or "grok-2-latest",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": human_prompt},
            ],
            "temperature": temperatura,
        }
        async with httpx.AsyncClient(timeout=60, verify=False) as client:
            response = await client.post(f"{provider_cfg['base_url']}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            dados = response.json()
            conteudo = dados.get("choices", [{}])[0].get("message", {}).get("content", "")
            if isinstance(conteudo, list):
                return "".join(part.get("text", "") for part in conteudo if isinstance(part, dict))
            return str(conteudo)

    api_key = provider_cfg.get("api_key")
    if not api_key:
        raise RuntimeError("Nenhuma chave de IA configurada. Defina GROK_API_KEY ou GROQ_API_KEY.")

    model_name = provider_cfg.get("model") or fallback_model or "openai/gpt-oss-20b"
    llm = ChatGroq(model=model_name, temperature=temperatura, groq_api_key=api_key)
    resposta = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt),
    ])
    return str(resposta.content)


def _construir_explicacao_erros(respostas_aluno: list, gabarito: list) -> list[str]:
    explicacoes = []
    for indice, (resposta_aluno, resposta_correta) in enumerate(zip(respostas_aluno, gabarito), start=1):
        if resposta_aluno == resposta_correta:
            continue

        if isinstance(resposta_aluno, str) and "/" in resposta_aluno and isinstance(resposta_correta, str) and "/" in resposta_correta:
            explicacao = (
                f"Na questão {indice}, a solução correta era {resposta_correta}. "
                f"O processo é simplificar ou reduzir a fração dividindo numerador e denominador pelo mesmo número. "
                f"Exemplo: 4/8 = (4÷4)/(8÷4) = 1/2. Sua resposta foi {resposta_aluno}; revise esse passo e repita o cálculo para fixar o método."
            )
        else:
            explicacao = (
                f"Na questão {indice}, a solução correta era {resposta_correta}. "
                f"O processo é identificar a regra do exercício, comparar as alternativas e confirmar qual resposta atende ao enunciado. "
                f"Sua resposta foi {resposta_aluno}; refaça o raciocínio e pratique mais exercícios parecidos para consolidar a aprendizagem."
            )

        explicacoes.append(explicacao)

    if not explicacoes:
        return [
            "Você acertou todas as questões. Continue praticando para consolidar o conhecimento e reforçar a confiança."
        ]

    return explicacoes[:2]


def _normalizar_feedback_pedagogico(conteudo_resposta: str, nota: float, respostas_aluno: list, gabarito: list) -> dict:
    texto = (conteudo_resposta or "").strip()
    if not texto:
        texto = "O aluno demonstrou esforço e precisa reforçar alguns conteúdos básicos."

    texto_limpo = re.sub(r"\s+", " ", texto)
    frases = [parte.strip(" -•*\n") for parte in re.split(r"(?<=[.!?])\s+|\n+", texto_limpo) if parte.strip()]
    frases = [f for f in frases if len(f) > 25]

    explicacoes_erros = _construir_explicacao_erros(respostas_aluno, gabarito)

    if len(frases) >= 2:
        pontos_fortes = frases[:2]
        pontos_atencao = explicacoes_erros + (frases[2:4] if len(frases) > 2 else [])
    else:
        pontos_fortes = [
            "O aluno demonstrou esforço e evolução ao responder a maior parte dos itens.",
            "Há um bom nível de engajamento com a atividade proposta."
        ]
        pontos_atencao = explicacoes_erros

    if nota >= 7:
        recomendacao = "Mantenha o ritmo de estudo e revise os tópicos que ainda geraram maior dúvida para consolidar a aprendizagem."
    elif nota >= 5:
        recomendacao = "Organize uma revisão focada nos itens mais desafiadores e retome os conceitos-chave antes da próxima avaliação."
    else:
        recomendacao = "Recomece pela revisão dos conteúdos fundamentais e pratique exercícios semelhantes para fortalecer a base."

    explicacoes_erros = _construir_explicacao_erros(respostas_aluno, gabarito)
    return {
        "pontos_fortes": pontos_fortes,
        "pontos_atencao": (pontos_atencao or explicacoes_erros)[:2],
        "solucao_correta": explicacoes_erros,
        "recomendacao_estudo": recomendacao,
    }


def _mensagem_erro_ia(exc: Exception) -> str:
    msg = str(exc).lower()
    if "429" in msg or "rate limit" in msg or "too many requests" in msg:
        return "Limite de uso da IA atingido. Aguarde alguns minutos e tente novamente."
    if "401" in msg or "invalid api key" in msg or "unauthorized" in msg:
        return "A chave da IA está inválida, expirada ou não corresponde ao provedor configurado."
    if "400" in msg or "bad request" in msg:
        return "A IA recusou a solicitação. Verifique o modelo e a configuração do provedor."
    return "A IA não respondeu corretamente no momento. Tente novamente em alguns instantes."


async def gerar_plano_ia(
    tema_aula: str,
    objetivos: list[str] | None = None,
    ano: str = "Ensino Fundamental",
    nivel: str = "Básico",
    duracao: str = "40 min",
    disciplina: str | None = None,
    habilidades_bncc: list[str] | None = None,
    escola_id: int | None = None,
) -> dict:
    objetivos_lista = objetivos or ["Reconhecer os conceitos principais do tema.", "Aplicar o conteúdo em exercícios simples."]
    disciplina_nome = disciplina or "Geral"
    prefixo_ano = "EF" if "fundamental" in ano.lower() or "ano" in ano.lower() else "EM"
    bncc_padrao = habilidades_bncc or [
        f"{prefixo_ano}07MA04: Construir raciocínio lógico e resolver problemas com {tema_aula}.",
        f"{prefixo_ano}07MA09: Utilizar a representação matemática para formular conclusões e conexões práticas."
    ]

    plano_fallback = {
        "titulo": f"Plano de aula: {tema_aula}",
        "disciplina": disciplina_nome,
        "ano": ano,
        "nivel": nivel,
        "duracao": duracao,
        "habilidades_bncc": bncc_padrao,
        "objetivos": objetivos_lista,
        "sequencia": [
            "1. Abertura com revisão rápida do tema e diagnóstico inicial.",
            "2. Explicação de conceitos-chave com exemplos simples e contextualizados.",
            "3. Prática guiada com exercícios de nível básico e intermediário.",
            "4. Correção coletiva com foco no raciocínio e na solução correta.",
            "5. Fechamento com atividade de reforço e acompanhamento individual."
        ],
        "recursos": ["Quadro ou slides do tema", "Exercícios impressos ou digitais", "Lista de revisão para apoio pedagógico"],
        "avaliacao": "Observar a participação dos alunos, a qualidade do raciocínio e os erros mais recorrentes para planejar o próximo reforço.",
    }

    if _resolve_provider_config(escola_id)["provider"] == "none":
        plano_fallback["aviso_ia"] = "Nenhuma chave de IA configurada. Defina GROK_API_KEY ou GROQ_API_KEY para gerar conteúdo com IA."
        return plano_fallback

    system_prompt = (
        "Você é um especialista em planejamento pedagógico alinhado às diretrizes educacionais e à BNCC (Base Nacional Comum Curricular) do Brasil. "
        "Gere um plano de aula objetivo, prático, sequencial e cite 1 a 3 códigos oficiais de habilidades da BNCC (ex: EF07MA04, EF08CI02, EM13MAT101) condizentes com o tema, série e componente informados. "
        "Retorne APENAS um JSON válido com os campos: titulo, disciplina, ano, habilidades_bncc (lista de strings com código e descrição), objetivos, sequencia (lista de etapas), recursos (lista) e avaliacao."
    )
    human_prompt = (
        f"Tema: {tema_aula}\n"
        f"Disciplina: {disciplina_nome}\n"
        f"Ano/Série: {ano}\n"
        f"Nível: {nivel}\n"
        f"Duração: {duracao}\n"
        f"Objetivos: {objetivos_lista}\n"
        f"Habilidades BNCC sugeridas: {habilidades_bncc or 'Inferir códigos oficiais adequados'}"
    )

    ultimo_erro = None
    for modelo in _listar_modelos_candidates():
        try:
            conteudo = await _chamada_llm_json(system_prompt, human_prompt, temperatura=0.2, fallback_model=modelo, escola_id=escola_id)
            conteudo = conteudo.strip()
            if conteudo.startswith("```"):
                conteudo = conteudo.replace("```json", "").replace("```", "").strip()
            if "titulo" in conteudo.lower() and "objetivos" in conteudo.lower():
                dados = json.loads(conteudo)
                if "habilidades_bncc" not in dados or not dados["habilidades_bncc"]:
                    dados["habilidades_bncc"] = bncc_padrao
                return dados
        except Exception as exc:
            ultimo_erro = exc
            logging.warning(f"IA-PLANO | Modelo {modelo} falhou: {exc}")
            continue

    plano_fallback["aviso_ia"] = _mensagem_erro_ia(ultimo_erro) if ultimo_erro else "A IA não está disponível no momento. Foi aplicado o conteúdo de fallback pedagógico."
    return plano_fallback


async def gerar_quiz_ia(
    tema: str,
    objetivo: str,
    quantidade: int = 5,
    nivel: str = "Básico",
    disciplina: str | None = None,
    habilidades_bncc: list[str] | None = None,
    escola_id: int | None = None,
) -> dict:
    if quantidade <= 0:
        quantidade = 5
    bncc_padrao = habilidades_bncc or [
        f"BNCC-HAB: Identificar e aplicar as noções centrais de {tema} na resolução de questões objetivas."
    ]
    perguntas_padrao = [
        {
            "pergunta": f"Qual é a melhor forma de resolver um problema relacionado a {tema}?",
            "opcoes": ["Aplicar a regra do tema passo a passo", "Ignorar o enunciado", "Escolher aleatoriamente", "Não responder"],
            "resposta_correta": "Aplicar a regra do tema passo a passo",
            "explicacao": f"A resposta correta exige compreender o conceito central de {tema} e aplicar a lógica do conteúdo de forma ordenada."
        },
        {
            "pergunta": f"O que evidencia maior domínio de {tema}?",
            "opcoes": ["Justificar a resposta com o raciocínio", "Responder sem explicar", "Trocar os termos", "Pular a etapa"],
            "resposta_correta": "Justificar a resposta com o raciocínio",
            "explicacao": f"Em {tema}, o raciocínio e a justificativa são fundamentais para mostrar que o aluno compreendeu a ideia principal."
        },
    ]

    quiz_fallback = {
        "tema": tema,
        "objetivo": objetivo,
        "habilidades_bncc": bncc_padrao,
        "perguntas": perguntas_padrao[:max(2, min(quantidade, 5))],
    }

    if _resolve_provider_config(escola_id)["provider"] == "none":
        quiz_fallback["aviso_ia"] = "Nenhuma chave de IA configurada. Defina GROK_API_KEY ou GROQ_API_KEY para gerar conteúdo com IA."
        return quiz_fallback

    system_prompt = (
        "Você é um especialista em elaboração de avaliações diagnósticas e formativas alinhadas à BNCC. "
        "Gere um quiz didático em JSON com os campos: "
        "- tema (string)\n"
        "- objetivo (string)\n"
        "- habilidades_bncc (lista com 1 ou 2 códigos oficiais da BNCC e descrição)\n"
        f"- perguntas (lista com EXATAMENTE {quantidade} objetos, cada qual contendo: pergunta, opcoes [lista com 4 strings], resposta_correta [string idêntica a uma das opções], explicacao [justificativa didática]).\n"
        f"MUITO IMPORTANTE: O nível de dificuldade das perguntas DEVE SER: {nivel}. Adapte o vocabulário e a complexidade para esse nível.\n"
        "Retorne APENAS JSON válido sem marcações extras."
    )
    human_prompt = (
        f"Tema: {tema}\n"
        f"Objetivo: {objetivo}\n"
        f"Disciplina: {disciplina or 'Geral'}\n"
        f"Nível: {nivel}\n"
        f"Quantidade: {quantidade}\n"
    )

    ultimo_erro = None
    for modelo in _listar_modelos_candidates():
        try:
            conteudo = await _chamada_llm_json(system_prompt, human_prompt, temperatura=0.2, fallback_model=modelo, escola_id=escola_id)
            conteudo = conteudo.strip()
            if conteudo.startswith("```"):
                conteudo = conteudo.replace("```json", "").replace("```", "").strip()
            if "pergunta" in conteudo.lower():
                parsed = json.loads(conteudo)
                if isinstance(parsed, dict) and "perguntas" in parsed:
                    if "habilidades_bncc" not in parsed:
                        parsed["habilidades_bncc"] = bncc_padrao
                    parsed["perguntas"] = parsed["perguntas"][:quantidade]
                    return parsed
                if isinstance(parsed, list):
                    return {"tema": tema, "objetivo": objetivo, "habilidades_bncc": bncc_padrao, "perguntas": parsed[:quantidade]}
        except Exception as exc:
            ultimo_erro = exc
            logging.warning(f"IA-QUIZ | Modelo {modelo} falhou: {exc}")
            continue

    quiz_fallback["aviso_ia"] = _mensagem_erro_ia(ultimo_erro) if ultimo_erro else "A IA não está disponível no momento. Foi aplicado o conteúdo de fallback pedagógico."
    return quiz_fallback


async def regenerar_questao_ia(
    tema: str,
    objetivo: str = "Aplicar os conceitos do tema.",
    nivel: str = "Básico",
    pergunta_anterior: str | None = None,
    escola_id: int | None = None,
) -> dict:
    pergunta_fallback = {
        "pergunta": f"Ao estudar {tema}, qual atitude demonstra aplicação correta do método?",
        "opcoes": [
            "Conferir cada etapa do cálculo ou raciocínio",
            "Preencher sem ler as alternativas",
            "Mudar de assunto sem terminar",
            "Ignorar as instruções da questão"
        ],
        "resposta_correta": "Conferir cada etapa do cálculo ou raciocínio",
        "explicacao": f"Para resolver itens sobre {tema}, a verificação metódica dos passos é a chave para o acerto."
    }

    if _resolve_provider_config(escola_id)["provider"] == "none":
        return pergunta_fallback

    system_prompt = (
        "Você é um especialista em avaliações escolares. "
        "Gere UMA única questão alternativa inovadora e inédita sobre o tema e nível informados. "
        "Retorne APENAS um objeto JSON com as chaves: pergunta, opcoes (array de exatamente 4 strings), resposta_correta (string idêntica a uma das opções), explicacao."
    )
    human_prompt = (
        f"Tema: {tema}\n"
        f"Objetivo: {objetivo}\n"
        f"Nível: {nivel}\n"
        f"Evitar repetir ou ser similar a: {pergunta_anterior or 'Nenhuma'}"
    )

    for modelo in _listar_modelos_candidates():
        try:
            conteudo = await _chamada_llm_json(system_prompt, human_prompt, temperatura=0.4, fallback_model=modelo, escola_id=escola_id)
            conteudo = conteudo.strip()
            if conteudo.startswith("```"):
                conteudo = conteudo.replace("```json", "").replace("```", "").strip()
            dados = json.loads(conteudo)
            if isinstance(dados, dict) and "pergunta" in dados and "opcoes" in dados:
                return dados
        except Exception as exc:
            logging.warning(f"IA-REGEN-QUESTAO | Modelo {modelo} falhou: {exc}")
            continue

    return pergunta_fallback


async def gerar_dica_socratica(
    pergunta: str,
    resposta_aluno: str,
    tema: str | None = None,
    escola_id: int | None = None,
) -> dict:
    dica_fallback = {
        "dica": "Observe com atenção as palavras-chave do enunciado e compare cada alternativa com o raciocínio principal.",
        "pergunta_orientadora": "Qual é a relação direta entre o que o enunciado pede e as partes que você considerou?",
    }

    if _resolve_provider_config(escola_id)["provider"] == "none":
        return dica_fallback

    system_prompt = (
        "Você é um tutor pedagógico socrático do EduCollab. "
        "Um estudante tentou responder a uma questão e está com dúvida ou errou. "
        "NUNCA dê a resposta final nem diga qual letra é a correta. "
        "Forneça: 1) uma dica amigável e estimulante em 1 ou 2 frases curtas; 2) uma pergunta orientadora reflexiva que o ajude a pensar. "
        "Retorne APENAS um JSON com as chaves 'dica' e 'pergunta_orientadora'."
    )
    human_prompt = (
        f"Questão: {pergunta}\n"
        f"Resposta tentada pelo aluno: {resposta_aluno}\n"
        f"Tema: {tema or 'Conteúdo escolar'}"
    )

    for modelo in _listar_modelos_candidates():
        try:
            conteudo = await _chamada_llm_json(system_prompt, human_prompt, temperatura=0.3, fallback_model=modelo, escola_id=escola_id)
            conteudo = conteudo.strip()
            if conteudo.startswith("```"):
                conteudo = conteudo.replace("```json", "").replace("```", "").strip()
            dados = json.loads(conteudo)
            if isinstance(dados, dict) and "dica" in dados:
                return dados
        except Exception as exc:
            logging.warning(f"IA-DICA-SOCRATICA | Modelo {modelo} falhou: {exc}")
            continue

    return dica_fallback


async def analisar_raio_x_turma_ia(
    turma_nome: str,
    tema_quiz: str,
    total_alunos: int,
    media_turma: float,
    erros_por_questao: list[dict],
    escola_id: int | None = None,
) -> dict:
    diagnostico_fallback = {
        "resumo_desempenho": f"A turma {turma_nome} obteve média {round(media_turma, 1)} no tema {tema_quiz}. O engajamento foi positivo com {total_alunos} submissões.",
        "principais_dificuldades": [
            "Interpretação detalhada dos termos e enunciados das questões.",
            "Fixação dos passos de simplificação e validação de resultados."
        ],
        "sugestoes_proxima_aula": [
            "Iniciar a próxima aula com uma revisão prática de 10 minutos focada nas questões com maior índice de erro.",
            "Propor resolução em duplas para incentivar a troca de raciocínios.",
            "Disponibilizar a mini-trilha de reforço individual para os estudantes com rendimento abaixo da média."
        ]
    }

    if _resolve_provider_config(escola_id)["provider"] == "none":
        return diagnostico_fallback

    system_prompt = (
        "Você é um consultor pedagógico institucional de apoio ao professor. "
        "Analise os dados reais de desempenho de uma turma em um quiz e produza um diagnóstico executivo acolhedor e acionável. "
        "Retorne APENAS um JSON com os campos: 'resumo_desempenho' (string), 'principais_dificuldades' (lista de strings), 'sugestoes_proxima_aula' (lista de 2 a 3 ações práticas para o professor)."
    )
    human_prompt = (
        f"Turma: {turma_nome}\n"
        f"Tema avaliado: {tema_quiz}\n"
        f"Total de submissões: {total_alunos}\n"
        f"Média da turma: {round(media_turma, 1)} de 10.0\n"
        f"Distribuição de erros por questão: {json.dumps(erros_por_questao, ensure_ascii=False)}"
    )

    for modelo in _listar_modelos_candidates():
        try:
            conteudo = await _chamada_llm_json(system_prompt, human_prompt, temperatura=0.3, fallback_model=modelo, escola_id=escola_id)
            conteudo = conteudo.strip()
            if conteudo.startswith("```"):
                conteudo = conteudo.replace("```json", "").replace("```", "").strip()
            dados = json.loads(conteudo)
            if isinstance(dados, dict) and "resumo_desempenho" in dados:
                return dados
        except Exception as exc:
            logging.warning(f"IA-RAIO-X-TURMA | Modelo {modelo} falhou: {exc}")
            continue

    return diagnostico_fallback


async def processar_feedback_llm(nota: float, respostas_aluno: list, gabarito: list, escola_id: int | None = None) -> dict:
    logging.info(f"LLM ENGINE | Iniciando inferência para nota {nota} via provedor de IA")

    provider_cfg = _resolve_provider_config(escola_id)
    if provider_cfg["provider"] == "none":
        logging.error("LLM ENGINE | Nenhuma chave de IA configurada. Defina GROK_API_KEY ou GROQ_API_KEY.")
        return {
            "pontos_fortes": ["Submissão registada."],
            "pontos_atencao": ["Chave da API de IA ausente. Configure GROK_API_KEY ou GROQ_API_KEY."],
            "recomendacao_estudo": "Verifique a configuração do ambiente do backend."
        }

    modelos_candidates = _listar_modelos_candidates()
    system_prompt = (
        "Você é um tutor pedagógico do EduCollab. "
        "Responda em português claro, com 2 pontos fortes, 2 pontos de atenção e 1 recomendação de estudo. "
        "O texto deve ser educativo, direto e motivador, sem listar uma estrutura rígida de cabeçalhos. "
        "Foque no desempenho do aluno, no que ele acertou e no que precisa reforçar."
    )

    human_prompt = (
        f"Nota Final: {nota}\n"
        f"Gabarito Oficial: {gabarito}\n"
        f"Respostas do Aluno: {respostas_aluno}\n"
        "Elabore uma avaliação construtiva e pedagógica para o aluno."
    )

    ultimo_erro = None
    for modelo in modelos_candidates:
        try:
            if provider_cfg["provider"] == "grok":
                conteudo_resposta = await _chamada_llm_json(system_prompt, human_prompt, temperatura=0.3, fallback_model=modelo, escola_id=escola_id)
            else:
                llm = ChatGroq(model=modelo, temperature=0.3, groq_api_key=provider_cfg["api_key"])
                response = await llm.ainvoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=human_prompt),
                ])
                conteudo_resposta = response.content

            logging.info(f"LLM ENGINE | Sucesso na geração do feedback via {provider_cfg['provider']} usando o modelo: {modelo}")
            return _normalizar_feedback_pedagogico(conteudo_resposta, nota, respostas_aluno, gabarito)
        except Exception as e:
            ultimo_erro = e
            texto_erro = str(e).lower()
            if "model_not_found" in texto_erro or "does not exist or you do not have access" in texto_erro:
                logging.warning(f"LLM ENGINE | Modelo Groq indisponível ({modelo}). Tentando próximo modelo.")
                continue
            import traceback
            erro_detalhado = str(traceback.format_exc())
            logging.error(f"LLM ENGINE ERRO COMPLETO: {erro_detalhado}")
            return {
                "pontos_fortes": ["Submissão registada."],
                "pontos_atencao": [f"Detalhe técnico: {str(e)[:300]}"],
                "recomendacao_estudo": "Consulte o painel de controlo ou tente novamente."
            }

    import traceback
    erro_detalhado = str(traceback.format_exc())
    logging.error(f"LLM ENGINE ERRO COMPLETO: {erro_detalhado}")
    return {
        "pontos_fortes": ["Submissão registada."],
        "pontos_atencao": [f"Detalhe técnico: {str(ultimo_erro)[:300]}"],
        "recomendacao_estudo": "Consulte o painel de controlo ou tente novamente."
    }

async def chat_tutor_livre_ia(mensagem: str, historico: list, escola_id: int | None = None) -> str:
    system_prompt = """Você é um Tutor Socrático amigável e encorajador para alunos do ensino fundamental e médio.
Sua regra de ouro: NUNCA dê a resposta pronta ou faça o trabalho pelo aluno.
Seu objetivo é fazer o aluno pensar. Use perguntas orientadoras, analogias simples e encorajamento.
Responda sempre de forma curta e direta (máx 2-3 parágrafos curtos)."""

    # Formatar o histórico para o prompt
    historico_texto = "\n".join([f"{msg['role']}: {msg['content']}" for msg in historico])
    
    human_prompt = f"""Histórico recente da conversa:
{historico_texto}

Nova mensagem do aluno: {mensagem}

Responda no papel de Tutor Socrático. Formato obrigatório: JSON {{ "resposta": "..." }}"""

    resultado_str = await _chamada_llm_json(system_prompt, human_prompt, temperatura=0.6, escola_id=escola_id)
    try:
        import json
        dados = json.loads(resultado_str)
        return dados.get("resposta", "Me conte mais sobre o que você está estudando hoje.")
    except Exception:
        return "Tive um problema ao formular a resposta. Pode tentar perguntar de outra forma?"

async def chat_copiloto_professor(escola_id: int, mensagem: str, historico: list) -> str:
    system_prompt = """Você é o Copiloto Pedagógico EduCollab, um assistente especializado em educação e pedagogia.
Seu objetivo é ajudar professores a criar planos de aula, gerar questões, analisar dados preditivos da turma, sugerir agrupamentos produtivos e responder a qualquer dúvida educacional.
Responda de forma clara, prática e no formato de texto limpo (Markdown). Seja sempre encorajador e consultivo."""
    
    historico_texto = "\n".join([f"{msg['role']}: {msg['content']}" for msg in historico])
    human_prompt = f"""Histórico da conversa:
{historico_texto}

Nova mensagem do professor: {mensagem}

Formato OBRIGATÓRIO de saída: JSON {{"resposta": "sua resposta em markdown aqui"}}"""

    resultado_str = await _chamada_llm_json(system_prompt, human_prompt, temperatura=0.7, escola_id=escola_id)
    try:
        import json
        dados = json.loads(resultado_str)
        return dados.get("resposta", resultado_str)
    except:
        return resultado_str
