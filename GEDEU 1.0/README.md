# GEDEU 1.0 - Gerenciador de Equipes Desportivas da UnB

## Descrição do Projeto
Sistema web para gerenciamento de equipes desportivas da Universidade de Brasília, desenvolvido como projeto acadêmico para a disciplina de Bancos de Dados 2025.1 Noturna.

## Estrutura do Projeto

### Arquivos Principais
- **`app.py`** - Aplicação Flask principal com todas as rotas e funcionalidades
- **`GEDEU.sql`** - Script de criação do banco de dados e estrutura das tabelas
- **`install_views.sql`** - Script para criação das views do sistema (com documentação)
- **`install_procedures.sql`** - Script para criação das procedures (com documentação)

### Diretórios
- **`static/`** - Arquivos estáticos (CSS, imagens)
- **`templates/`** - Templates HTML do Flask
- **`uploads/`** - Arquivos de upload (documentos PDF)


## Funcionalidades Principais

### Gestão de Dados
- Visualização de todas as tabelas do sistema
- Operações CRUD
- Upload de documentos PDF

### Relatórios e Consultas
- **Dashboard de Equipes**: Estatísticas consolidadas por equipe
- **Ranking de Atletas**: Classificação por presença em atividades
- **Relatório de Presença**: Análise detalhada por equipe
- **Estatísticas de Atleta**: Métricas individuais completas

### Views Disponíveis
- `dashboard_equipes` - Visão geral das equipes
- `ranking_atletas` - Ranking de participação

### Procedures Disponíveis
- `relatorio_presenca_equipe(equipe_id)` - Relatório de presença
- `estatisticas_atleta(atleta_id)` - Estatísticas individuais

## Estrutura do Banco de Dados

### Tabelas Principais
1. **Modalidade** - Esportes e categorias
2. **Local** - Locais de eventos e treinamentos
3. **Evento** - Eventos esportivos
4. **Campeonato** - Campeonatos específicos
5. **Equipe** - Equipes participantes
6. **Documento** - Documentos PDF armazenados como BLOB no banco
7. **Atleta** - Atletas das equipes
8. **Treinador** - Treinadores das equipes
9. **Partida** - Partidas realizadas
10. **Treinamento** - Sessões de treinamento
11. **Presenca_Partida** - Controle de presença em partidas
12. **Presenca_Treinamento** - Controle de presença em treinamentos
13. **Participacao_Campeonato** - Participação de equipes em campeonatos

## Tecnologias Utilizadas
- **Backend**: Python + Flask
- **Banco de Dados**: PostgreSQL
- **Frontend**: HTML5 + CSS3