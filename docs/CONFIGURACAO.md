# Guia de configuração do laboratório (AWS Ubuntu + GitHub Actions)

## 1. Repositório
1. Crie um novo repositório a partir deste starter (com o histórico próprio do grupo).
2. Ative Actions e mantenha `main` protegida quando o plano da conta permitir.
3. Crie branch `feature/...`, envie PR e só integre após CI passar.

## 2. AWS EC2
1. Crie instância **Ubuntu Server 24.04 LTS**, arquitetura x86_64, com IP público e chave SSH. Verifique preços/limites/créditos antes de iniciar.
2. Security Group: HTTP TCP/80 de fontes permitidas para testar; SSH TCP/22 **apenas do seu próprio IP**, só para manutenção manual. Como o CD roda em um runner auto-hospedado dentro da própria EC2 (ver item 4), **não é preciso abrir SSH para o runner do GitHub Actions** — o problema do IP variável do runner hospedado deixa de existir. **Não deixe SSH aberto para toda a internet.**
3. Conecte com SSH (do seu IP) e execute `bash scripts/setup-ec2-ubuntu.sh` (copie o script ou clone o repositório na instância). Faça logout/login e teste `docker ps` sem sudo.
4. Instale o runner auto-hospedado: no repositório GitHub, acesse Settings > Actions > Runners > New self-hosted runner > Linux x64, e execute na EC2 os comandos exibidos (baixa o pacote, `./config.sh --url ... --token ...`). Depois rode como serviço com `sudo ./svc.sh install && sudo ./svc.sh start`, para seguir ativo mesmo após desconectar o SSH. Confirme que o runner aparece como "Idle" na lista de runners do repositório. O usuário que executa o runner precisa estar no grupo `docker` (feito pelo passo 3).
5. Certifique-se que a porta 80 está livre. Execute deploy manual primeiro, se necessário.

## 3. GitHub
Em Settings > Secrets and variables > Actions não é necessário nenhum secret de SSH (`EC2_HOST`, `EC2_SSH_KEY`, `EC2_KNOWN_HOSTS`, `EC2_USER`) — o CD roda localmente no runner auto-hospedado da EC2, sem conexão remota. Crie environment `production` para aprovações (se disponível).
Em Settings > Actions > Runners, mantenha o serviço do runner (`actions.runner.*`) sempre ativo na EC2; se ele cair, os jobs do CD ficam parados em "Queued".

## 4. Registry GHCR
A CI publica imagem `ghcr.io/OWNER/REPO:COMMIT_SHA` após `push` na main. Para simplificar o laboratório, nas configurações do pacote GitHub mude a visibilidade da imagem para **Public**, de modo que EC2 execute `docker pull` sem credenciais persistentes. Não publique dados sensíveis na imagem.

## 5. Validação
- Crie PR: apenas testes/build; sem publicação ou deploy.
- Merge para `main`: CI publica imagem; evento `workflow_run` inicia CD.
- Acesse `http://IP_PUBLICO/health`, `http://IP_PUBLICO/tasks`.
- Faça nova mudança pela branch e PR e comprove novo deploy automático.
- Faça screenshot dos runs e registre URL/commit no relatório.

## 6. Diagnóstico
- Actions falhou em `docker push`: verifique `packages: write`, permissões de Actions e configuração GHCR.
- `docker pull` falhou na EC2: confira se pacote está público e se tag SHA existe.
- Job do CD fica "Queued" sem rodar: o runner auto-hospedado está offline — na EC2, confira `sudo ./svc.sh status` (ou `systemctl status actions.runner.*`) e reinicie o serviço.
- Falha HTTP: verifique SG porta 80, endereço, `docker ps` e `docker logs cloud-tasks-api`.
- **Observação:** como o CD roda em um runner auto-hospedado dentro da própria EC2, não há necessidade de abrir a porta 22 para IPs do runner do GitHub Actions — isso elimina o problema do IP variável do runner hospedado.

## 7. Custos e encerramento
Desligar nem sempre elimina custo de EBS e IP; após a apresentação, exclua instância, volumes e recursos alocados conforme orientação docente.
