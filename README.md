# 🎓 EduCollab - Plataforma Educacional com Inteligência Artificial

![License](https://img.shields.io/badge/license-MIT-blue)
![React](https://img.shields.io/badge/React-18.x-61DAFB?logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

O **EduCollab** é uma plataforma SaaS (Software as a Service) educacional multi-tenant construída para revolucionar a dinâmica em sala de aula. Ele atua em três frentes principais: oferecendo painéis executivos para Diretores, atuando como Copiloto Pedagógico para Professores e servindo como um Tutor Socrático personalizado para Alunos.

---

## ✨ Principais Funcionalidades

### 🏢 Para Gestores (Admin)
- **Dashboard Multi-Tenant:** Gestão centralizada de múltiplas escolas.
- **Inteligência Executiva:** Previsão de custos de IA, risco de evasão tecnológica (churn) e projeção de desempenho acadêmico macro.
- **Analista IA da Rede:** Chatbot executivo que cruza dados e sugere ações gerenciais em tempo real.
- **Gestão de Custos:** Acompanhamento de tokens e faturamento por escola e modelo (Grok, LLaMA via Groq, etc).

### 👨‍🏫 Para Professores
- **Copiloto Pedagógico:** Geração instantânea de Planos de Aula alinhados à BNCC.
- **Criação de Avaliações com IA:** Geração de Quizzes diagnósticos com controle humano e personalização de nível de dificuldade.
- **Raio-X Preditivo:** Painel que cruza as notas para gerar alertas de alunos em risco e sugestão de agrupamentos produtivos.
- **Assistente 24/7:** Chat flutuante exclusivo para ajudar a criar questões ou adaptar metodologias para alunos atípicos.

### 👩‍🎓 Para Alunos
- **Tutor Socrático de Bolso:** IA treinada para guiar o raciocínio sem entregar respostas prontas.
- **Trilhas e Quizzes Gamificados:** Gráficos de evolução (XP) e feedback estruturado após cada avaliação.
- **Revisão Inteligente:** Algoritmo que detecta notas baixas e oferece resumos proativos antes da próxima aula.

Não és um profissional técnico da área? Não se preocupe! Elaborei um passo a passo simples pra começar, basta clicar neste manual:

<a href="comece_por_aqui_apresentacao_educollab.html"><kbd><b>📄 Abrir Manual Educollab</b></kbd></a>

---

## 🛠️ Arquitetura e Tecnologias

O projeto utiliza uma arquitetura moderna separada em Frontend e Backend, orquestrada via Docker.

- **Frontend:** React.js, Vite, TailwindCSS, Recharts, Lucide Icons.
- **Backend:** Python, FastAPI, SQLAlchemy (ORM), Passlib (Bcrypt), JWT Auth.
- **Banco de Dados:** PostgreSQL.
- **Infraestrutura:** Docker & Docker Compose.
- **IA e LLMs:** Integração com modelos rápidos (Groq) e robustos (xAI/Grok) através de roteamento inteligente via `services.py`.

---

## 🚀 Como Executar o Projeto Localmente

### 1. Pré-requisitos
Certifique-se de ter o [Docker](https://www.docker.com/) e o [Docker Compose](https://docs.docker.com/compose/) instalados em sua máquina.

### 2. Configurando o Ambiente
Faça um clone do repositório e crie o seu arquivo de variáveis de ambiente:

```bash
git clone https://github.com/SEU_USUARIO/educollab.git
cd educollab
cp .env.example .env
```

Abra o arquivo `.env` e insira sua chave da IA de fallback (ex: Groq ou xAI) para permitir o uso imediato sem configuração pelo painel:
```env
GROQ_API_KEY=sua_chave_groq_aqui
```

### 3. Subindo os Containers
No terminal, na raiz do projeto, execute:
```bash
docker-compose up -d --build
```
Isso irá construir as imagens do PostgreSQL, do Backend (FastAPI) e do Frontend (React).

O sistema já executará automaticamente o script de `seed` no backend, populando o banco com escolas, professores, turmas e históricos de avaliação simulados.

### 4. Acessando a Plataforma
Abra o navegador e acesse: **http://localhost:5173**

**Credenciais de Teste (Demo):**
- **Administrador:** `admin@educollab.demo` | senha: `admin123`
- **Professor:** `professor@educollab.demo` | senha: `prof123`
- **Aluno:** `aluno@educollab.demo` | senha: `aluno123`

---

## 🛡️ Segurança e Boas Práticas
- **Nunca comite seu `.env`:** O arquivo `.gitignore` já está configurado para barrar credenciais sensíveis.
- **Senhas em Hash:** O banco de dados não armazena senhas em texto plano, utilizando Bcrypt para validação.
- **Chaves de IA Escolares:** As API Keys inseridas pelas escolas via painel são criptografadas por simetria antes de irem para o banco.

---
*Construído com paixão pela Educação e pela Tecnologia.* 🚀
