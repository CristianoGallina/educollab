# 🚀 Guia de Demonstração: Como testar o EduCollab no seu computador

Bem-vindo(a)! Se você é um professor, diretor ou avaliador e quer testar a plataforma **EduCollab** no seu próprio computador, este é o guia perfeito. 

Não se preocupe se você não for um programador. Nós mastigamos toda a parte "técnica" em **4 passos simples** para você ver a mágica da IA funcionando na sua frente.

---

## 🛠️ Parte 1: Ligando os Motores (Instalação)

O EduCollab é um sistema complexo (tem banco de dados, servidores e inteligência artificial), mas nós "empacotamos" tudo isso em uma caixa mágica chamada **Docker**. Você só precisa rodar essa caixa.

### Passo 1: Baixar o "Motor" (Docker)
1. Acesse o site oficial: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Baixe e instale o programa no seu computador (é só seguir clicando em *Avançar / Next*).
3. Abra o Docker Desktop e deixe-o rodando (ele vai ficar com um ícone perto do relógio do seu computador).

### Passo 2: Baixar o EduCollab
1. Acesse a página do projeto (GitHub).
2. Clique no botão verde **"Code"** e depois em **"Download ZIP"**.
3. Extraia/Descompacte essa pasta em um lugar fácil, como a sua *Área de Trabalho*.

### Passo 3: Adicionar sua Chave de IA (O Cérebro)
A plataforma usa o cérebro da Inteligência Artificial para gerar as aulas. Para funcionar, precisamos ligar a chave:
1. Entre na pasta que você acabou de extrair.
2. Lá dentro, existe um arquivo chamado `.env.example`. Renomeie ele para **`.env`** (basta apagar o ".example").
3. Abra esse arquivo `.env` com o Bloco de Notas e cole a sua chave gratuita do Groq na linha `GROQ_API_KEY=sua_chave_aqui`. *(Se não tiver uma, crie de graça em [console.groq.com](https://console.groq.com/keys)).*

### Passo 4: Ligar o Sistema
1. Abra o **Prompt de Comando** (no Windows, aperte Iniciar, digite `cmd` e dê Enter) ou o **Terminal** no Mac.
2. Navegue até a pasta onde você extraiu o projeto. *(Dica: digite `cd ` e arraste a pasta para dentro da tela preta, depois dê Enter).*
3. Digite o comando mágico para ligar tudo:
   ```bash
   docker-compose up -d
   ```
4. Espere uns minutinhos enquanto ele baixa e liga tudo.

---

## 💻 Parte 2: Acessando e Usando a Plataforma

Se você seguiu os passos acima, o seu computador acabou de virar uma escola inteligente!

### O Primeiro Login
Abra o navegador de internet (Chrome, Safari, etc.) e digite exatamente isso na barra de endereços:
👉 **http://localhost:5173**

Você verá a tela inicial do EduCollab! Como o sistema já cria uma escola "fictícia" cheia de dados para você testar, use as seguintes credenciais:

| Perfil | Email de Teste | Senha | O que você vai ver |
| :--- | :--- | :--- | :--- |
| **Professor** | `professor@educollab.demo` | `prof123` | Criação de planos de aula, quizzes e análise de alunos em risco. |
| **Aluno** | `aluno@educollab.demo` | `aluno123` | Gamificação, responder quizzes e usar o Tutor de Bolso (IA). |
| **Diretor (Admin)** | `admin@educollab.demo` | `admin123` | Painel de controle de custos da IA e saúde das escolas. |

---

## 👨‍🏫 Dica de Ouro: O que testar como Professor?
Para sentir o verdadeiro poder da plataforma, entre com a conta do **Professor** e faça este roteiro:
1. No menu esquerdo, clique em **Ferramentas de IA**.
2. Vá na aba **Quizzes**.
3. Escolha a turma, coloque "Nível Difícil" e digite o tema: *"Revolução Francesa"*.
4. Clique em Gerar. Veja a IA criar questões de múltipla escolha perfeitas, já com o gabarito justificado!
5. Depois, vá na tela inicial (Dashboard) e veja o painel de **Inteligência Preditiva**, que te avisa exatamente quais alunos estão com risco de reprovar baseando-se no histórico deles.

Boa diversão! A educação do futuro acaba de chegar no seu computador. 🚀
