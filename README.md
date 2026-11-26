# Twitter — API e execução completa

Este repositório contém a API REST em Django, PostgreSQL e Redis para a aplicação Twitter. O front-end React fica em outro repositório. Este guia reúne a execução local dos dois projetos, criação e ativação de conta, testes principais e uma opção de hospedagem gratuita com limitações.

## O que é necessário

- Git
- Docker Desktop com o Docker Compose v2 (Windows, macOS ou Linux)
- Node.js 22 e npm para o front-end
- Navegador atualizado

Não é necessário instalar Python, PostgreSQL ou Redis no computador para executar a opção com Docker. Para enviar e-mail real ou usar login do Google, consulte as seções opcionais; a execução local básica não exige conta paga, SMTP ou credencial Google.

## 2. Preparar o ambiente local

### Backend

Entre no projeto e crie o `.env` apenas se ele ainda não existir:

```powershell
cd $HOME\twitter-clone\twitter-backend
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Abra `.env` e confirme estes valores para Docker Compose:

```dotenv
ENV=development
TYPE_DATABASE=postgresql
DB_ENGINE=django.db.backends.postgresql
DB_NAME=twitter
DB_USER=twitter
DB_PASSWORD=escolha_uma_senha_local
DB_HOST=db
DB_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379
DOMAIN_FRONTEND=http://localhost:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000 http://127.0.0.1:3000
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Troque `DB_PASSWORD` por uma senha local sua. Não coloque esse arquivo no GitHub: `.env` está ignorado pelo Git. Se você já tem `.env`, não o substitua; confira/adicione as variáveis necessárias e mantenha sua `SECRET_KEY`.

Substitua também `SECRET_KEY` por uma chave aleatória para este ambiente. Gere uma string segura no PowerShell e copie o resultado para a linha `SECRET_KEY=` do `.env`:

```powershell
[Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(50)).TrimEnd('=').Replace('+','-').Replace('/','_')
```

### Front-end

Em outra janela do PowerShell:

```powershell
cd $HOME\twitter-clone\twitter-frontend
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Para execução local, o `.env` do front-end deve conter:

```dotenv
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
REACT_APP_DOMAIN=127.0.0.1:8000
REACT_APP_GOOGLE_CLIENT_ID=
REACT_APP_GOOGLE_CALLBACK_URL=http://localhost:3000/
```

O login por e-mail e senha funciona sem Google OAuth. Deixe `REACT_APP_GOOGLE_CLIENT_ID` vazio se não configurou um cliente Google; o botão Google depende dessa configuração e não é necessário para testar as demais funções.

## 3. Iniciar PostgreSQL, Redis e API

Na janela do backend:

```powershell
docker compose up -d --build
docker compose ps
```

Espere os três serviços (`api`, `db` e `redis`) aparecerem como `Up`. Verifique Redis e API:

```powershell
docker compose exec redis redis-cli ping
Invoke-RestMethod http://localhost:8000/health/
```

O Redis deve responder `PONG`; a API deve responder `status : ok`. O comando de inicialização da API aplica as migrações Django automaticamente. Na primeira inicialização, o PostgreSQL pode levar alguns segundos; se a API sair antes de o banco ficar pronto, rode:

```powershell
docker compose up -d api
docker compose logs --tail 100 api
```

Para acompanhar os registros em tempo real sem parar os serviços:

```powershell
docker compose logs -f api
```

Use `Ctrl+C` para sair da visualização de logs. Isso não deve ser confundido com parar todos os containers; para desligar o ambiente no fim do uso:

```powershell
docker compose down
```

O banco fica no volume `database` e permanece após `docker compose down`. Não use `docker compose down -v` se quiser conservar os dados.

## 4. Iniciar o front-end

Confirme que Node e npm estão disponíveis:

```powershell
node -v
npm.cmd -v
```

Se `node` não for reconhecido, instale Node.js 22 LTS, feche e reabra o PowerShell. Se a política do PowerShell bloquear `npm.ps1`, use `npm.cmd` como abaixo:

```powershell
cd $HOME\twitter-clone\twitter-frontend
npm.cmd ci
npm.cmd start
```

Abra [http://localhost:3000](http://localhost:3000). Mantenha o terminal do front-end aberto enquanto usa a aplicação. Para parar apenas o servidor React, pressione `Ctrl+C na janela em que executou npm.cmd start`.

## 5. Criar e ativar uma conta sem serviço de e-mail

No ambiente local, `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` escreve o e-mail de ativação nos logs da API. Isso permite validar o fluxo sem configurar Gmail, senha de app ou outro serviço de envio. A mensagem não chega a uma caixa de entrada.

1. Abra `http://localhost:3000`, selecione cadastro e crie uma conta com e-mail válido e senha que passe nas validações. Guarde a senha para entrar depois.
2. Na janela do backend, consulte os logs recentes:

   ```powershell
   cd $HOME\twitter-clone\twitter-backend
   docker compose logs --since 10m api
   ```

3. Nos logs, localize a mensagem `Activate your Twitter account` e copie o endereço que começa por `http://localhost:3000/auth/user/account/activation/`. Abra esse endereço no navegador. Não compartilhe os logs publicamente: o link contém o token temporário de ativação.
4. A página deve confirmar a ativação. Volte ao login e entre com o e-mail e a senha cadastrados.
5. Se a mensagem não estiver nos logs, tente cadastrar novamente com outro e-mail ou use **reenviar e-mail de ativação** na tela de confirmação; depois consulte os logs outra vez. Veja também `docker compose logs --tail 100 api` para localizar falhas.

O token de ativação tem validade limitada. Se expirou, solicite um novo pela interface. O endpoint de reenvio é `POST /api/auth/user/account/activation/resend/` com JSON `{ "email": "seu@email.com" }`.

## 6. Verificações funcionais recomendadas

Com a conta ativada, percorra estes fluxos na interface:

1. Entre e confirme que a rota inicial abre sem erros no Console do navegador.
2. Edite nome, foto e demais campos de perfil disponíveis; recarregue a página para verificar que os dados persistem.
3. Publique um post e confira se ele aparece no topo do feed.
4. Cadastre uma segunda conta em uma janela anônima, ative pelo link nos logs e siga/unfollow entre os dois perfis.
5. Publique pela segunda conta e confirme a ordem mais recente primeiro e que o feed considera as contas seguidas.
6. Teste curtir, comentar, repostar, salvar e as notificações; confirme a atualização e confira os logs se algo falhar.

Para executar os testes Django:

```powershell
cd $HOME\twitter-clone\twitter-backend
docker compose exec api python manage.py test
```

Para rodar apenas os testes de cadastro:

```powershell
docker compose exec api python manage.py test apps.authentication.tests.tests_views.test_signup_views
```

O build de produção do front-end pode ser conferido com:

```powershell
cd $HOME\twitter-clone\twitter-frontend
npm.cmd run build
```

## Endpoints de autenticação principais

| Método | Caminho | Função |
|---|---|---|
| `POST` | `/api/auth/user/signup/` | Criar conta e gerar mensagem/link de ativação |
| `POST` | `/api/auth/user/account/activation/` | Ativar conta usando `uidb64` e `token` enviados pela interface |
| `POST` | `/api/auth/user/account/activation/resend/` | Solicitar novamente a ativação |
| `POST` | `/api/auth/user/login/` | Login com e-mail e senha |
| `POST` | `/api/auth/user/request/reset-password/` | Solicitar redefinição de senha |
| `POST` | `/api/auth/user/reset-password/<uidb64>/<token>/` | Confirmar nova senha |
| `POST` | `/api/auth/user/change-password/` | Alterar senha autenticado |
| `POST` | `/api/auth/user/token/refresh/` | Renovar token JWT |

A documentação interativa da API fica em [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/).

## Login opcional com Google

O login Google só funciona depois de cadastrar credenciais próprias no Google Cloud; não há credenciais de demonstração embutidas. No cliente OAuth do tipo **Web application**, adicione `http://localhost:3000` em **Authorized JavaScript origins** e `http://localhost:3000/` em **Authorized redirect URIs**. A URI de redirecionamento precisa corresponder exatamente à configurada no aplicativo, incluindo esquema e barra final. [Documentação OAuth do Google](https://developers.google.com/identity/protocols/oauth2/web-server).

Defina o mesmo Client ID no `.env` dos dois projetos: `GOOGLE_CLIENT_ID` no backend e `REACT_APP_GOOGLE_CLIENT_ID` no front-end. Ponha o `GOOGLE_CLIENT_SECRET` somente no `.env` do backend. Em seguida, reinicie a API e o React como descrito abaixo. Nunca envie o Client Secret ao GitHub.

## Reiniciar após mudar configuração

Variáveis `REACT_APP_*` são lidas quando o React inicia; variáveis do backend vêm do `.env` carregado no container. Após editar:

```powershell
# Backend: na pasta twitter-backend
docker compose up -d --build api

# Front-end: pare o servidor com Ctrl+C e execute novamente na pasta twitter-frontend
npm.cmd start
```

Se mudou também usuário/senha/nome do PostgreSQL depois de já ter criado o volume, o banco não recria suas credenciais automaticamente. Para uma base local descartável e vazia, pare o ambiente e recrie o volume com cuidado; isso apaga os dados locais:

```powershell
docker compose down -v
docker compose up -d --build
```

## Diagnóstico rápido

| Sintoma | O que verificar |
|---|---|
| `npm` não reconhecido | Instale Node.js 22, reabra PowerShell e use `npm.cmd`. |
| `npm.ps1` bloqueado | Rode `npm.cmd ci` e `npm.cmd start`. |
| `Copy-Item .env.example .env` diz que não encontra o arquivo | Confirme que está na pasta `twitter-backend`; rode `Get-ChildItem -Force`. Não sobrescreva um `.env` existente. |
| Cadastro retorna erro de e-mail | Confirme `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`, recrie o container API e leia os logs da API. |
| `redis is not running` ou timeout de WebSocket | Rode `docker compose up -d`, confira `docker compose ps` e `docker compose exec redis redis-cli ping`. |
| Tela diz `WebSocket ... undefined` | Confirme o `REACT_APP_API_BASE_URL` no front-end; pare e inicie `npm.cmd start` de novo. |
| Cadastro aponta `404` em `:3000/api/...` | Verifique `REACT_APP_API_BASE_URL=http://127.0.0.1:8000` e reinicie o front-end. |
| `redirect_uri_mismatch` no Google | Compare origem e callback no Google Cloud com `REACT_APP_GOOGLE_CALLBACK_URL` e `DOMAIN_FRONTEND`; a barra final importa. |
| Imagem de perfil não carrega | A configuração de Cloudinary é opcional para o fluxo básico; uploads externos precisam de credenciais Cloudinary válidas. |
| API não inicia depois do banco | Aguarde `db` ficar `Up`, rode `docker compose up -d api` e leia `docker compose logs --tail 100 api`. |

Avisos do Compose sobre `version` ser obsoleto não indicam falha; a chave foi removida do arquivo atual. Para diagnosticar, veja `docker compose ps -a` e os logs dos serviços relevantes. Não publique logs que contenham links de ativação, tokens ou dados pessoais.

## Hospedagem gratuita (opcional)

Para testar uma URL pública sem contratar planos, os Blueprints estão configurados com recursos **Free** do Render. Faça a implantação nesta ordem:

1. Envie cada repositório para um GitHub seu ou conecte os repositórios públicos existentes ao Render.
2. Crie o Blueprint deste backend. Se pedir confirmação de plano, selecione **Free** na API, PostgreSQL e Key Value. O Blueprint chama a API `twitter-api`; anote a URL HTTPS efetivamente atribuída.
3. No formulário do Blueprint, para `DOMAIN_FRONTEND` e `CORS_ALLOWED_ORIGINS`, informe o domínio planejado do site estático, por exemplo `https://twitter-frontend.onrender.com`. Para `CSRF_TRUSTED_ORIGINS`, inclua o domínio do frontend e da API, separados por espaço. Depois confirme e aguarde a API/banco iniciarem. Não aceite upgrade ou recurso com preço.
4. Crie o site estático usando o `render.yaml` do frontend. Para `REACT_APP_API_BASE_URL`, informe o endereço HTTPS real da API, sem `/` no final. Se o endereço atribuído ao frontend diferir do que foi previsto, atualize `DOMAIN_FRONTEND`, `CORS_ALLOWED_ORIGINS` e `CSRF_TRUSTED_ORIGINS` no backend para o domínio real e faça novo deploy da API.
5. Aguarde os dois deploys, visite `/health/` na API e abra o domínio do frontend. Cadastro no modo `console.EmailBackend` escreve o link de ativação nos logs do backend; não envia e-mail.
6. Opcional Google OAuth em produção: no Google Cloud, autorize como JavaScript origin o domínio HTTPS real do frontend sem barra final e como redirect URI o mesmo domínio com `/` final. Configure `REACT_APP_GOOGLE_CLIENT_ID` e `REACT_APP_GOOGLE_CALLBACK_URL` no frontend; `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` e `DOMAIN_FRONTEND` no backend. O `DOMAIN_FRONTEND` fica sem a barra final. Faça novo deploy dos dois serviços para as variáveis surtirem efeito.

A hospedagem gratuita não mantém o backend disponível sem interrupção: o serviço web pode dormir por inatividade e reiniciar, a base PostgreSQL gratuita expira após 30 dias e o Redis gratuito perde os dados ao reiniciar. O serviço web gratuito tem 750 horas por workspace/mês; excesso de banda ou uso pode ter cobrança conforme regras do provedor. Confira o painel antes de criar recursos e não habilite upgrade pago. [Limites oficiais do plano gratuito](https://render.com/docs/free).

O Blueprint está configurado com planos gratuitos e backend no modo de e-mail de console. Nesse modo, cadastro/ativação pode ser conferido pelos logs do serviço, mas não envia mensagens para uma caixa de entrada. Para uso contínuo, dados duráveis e entrega real de e-mail sem limitações, seria necessário outro provedor/configuração; este guia não promete disponibilidade contínua ou armazenamento permanente no plano gratuito.

Sem as variáveis opcionais de Cloudinary, o backend inicia usando armazenamento local. No plano gratuito, arquivos enviados não são persistentes e não devem ser considerados disponíveis depois de reinício/redeploy; teste a aplicação sem depender de uploads de imagens.

Para rodar apenas no próprio computador, não é preciso criar conta em provedor de nuvem: Docker Desktop e Node.js são suficientes.

## Licença

Este projeto usa a licença [MIT](LICENSE).
