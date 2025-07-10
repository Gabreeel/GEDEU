-- VIEW 1: DASHBOARD_EQUIPES

-- Propósito: Fornece uma visão consolidada de cada equipe com estatísticas
--            de atletas, treinadores, participações e presenças
-- 
-- Como funciona:
-- - Agrega dados de múltiplas tabelas relacionadas a equipes
-- - Calcula totais de atletas ativos e treinadores por equipe
-- - Computa estatísticas de presença em treinamentos e partidas
-- - Mostra participações em campeonatos

CREATE OR REPLACE VIEW dashboard_equipes AS
SELECT 
    e.cod_equipe,
    e.nome_equipe,
    e.ano_fundacao,
    e.status_ativa,
    
    -- Contagem de atletas ativos na equipe
    COUNT(DISTINCT a.id_atleta) as total_atletas,
    
    -- Contagem de treinadores ativos na equipe
    COUNT(DISTINCT CASE WHEN t.status_ativo = true THEN t.id_treinador END) as total_treinadores,
    
    -- Contagem de participações em campeonatos
    COUNT(DISTINCT pc.cod_campeonato) as total_campeonatos,
    
    -- Estatísticas de presença em treinamentos
    COUNT(DISTINCT pt.cod_treinamento) as total_treinamentos,
    COALESCE(
        ROUND(
            (COUNT(CASE WHEN pt.presenca = true THEN 1 END) * 100.0 / 
             NULLIF(COUNT(pt.presenca), 0)), 2
        ), 0
    ) as percentual_presenca_treinamentos,
    
    -- Estatísticas de presença em partidas
    COUNT(DISTINCT pp.cod_partida) as total_partidas,
    COALESCE(
        ROUND(
            (COUNT(CASE WHEN pp.presenca = true THEN 1 END) * 100.0 / 
             NULLIF(COUNT(pp.presenca), 0)), 2
        ), 0
    ) as percentual_presenca_partidas

FROM Equipe e
LEFT JOIN Atleta a ON e.cod_equipe = a.cod_equipe
LEFT JOIN Treinador t ON e.cod_equipe = t.cod_equipe
LEFT JOIN Participacao_Campeonato pc ON e.cod_equipe = pc.cod_equipe
LEFT JOIN Presenca_Treinamento pt ON a.id_atleta = pt.id_atleta
LEFT JOIN Presenca_Partida pp ON a.id_atleta = pp.id_atleta

GROUP BY e.cod_equipe, e.nome_equipe, e.ano_fundacao, e.status_ativa
ORDER BY e.cod_equipe;


-- VIEW 2: RANKING_ATLETAS

-- Propósito: Cria um ranking de atletas baseado na frequência de participação
--            em treinamentos e partidas
-- 
-- Como funciona:
-- - Calcula estatísticas individuais de presença para cada atleta
-- - Computa percentuais de presença em treinamentos e partidas
-- - Calcula uma pontuação geral baseada na participação
-- - Ordena os atletas por desempenho de presença

CREATE OR REPLACE VIEW ranking_atletas AS
SELECT 
    a.id_atleta,
    a.nome_atleta,
    a.matricula_unb,
    a.curso,
    e.nome_equipe,
    
    -- Estatísticas de treinamentos
    COUNT(DISTINCT pt.cod_treinamento) as total_treinamentos_convocado,
    COUNT(CASE WHEN pt.presenca = true THEN 1 END) as presencas_treinamentos,
    COALESCE(
        ROUND(
            (COUNT(CASE WHEN pt.presenca = true THEN 1 END) * 100.0 / 
             NULLIF(COUNT(pt.cod_treinamento), 0)), 2
        ), 0
    ) as percentual_presenca_treinamentos,
    
    -- Estatísticas de partidas
    COUNT(DISTINCT pp.cod_partida) as total_partidas_convocado,
    COUNT(CASE WHEN pp.presenca = true THEN 1 END) as presencas_partidas,
    COALESCE(
        ROUND(
            (COUNT(CASE WHEN pp.presenca = true THEN 1 END) * 100.0 / 
             NULLIF(COUNT(pp.cod_partida), 0)), 2
        ), 0
    ) as percentual_presenca_partidas,
    
    -- Pontuação geral (média ponderada: 60% treinamentos + 40% partidas)
    COALESCE(
        ROUND(
            (COALESCE(
                (COUNT(CASE WHEN pt.presenca = true THEN 1 END) * 100.0 / 
                 NULLIF(COUNT(pt.cod_treinamento), 0)), 0
            ) * 0.6 + 
            COALESCE(
                (COUNT(CASE WHEN pp.presenca = true THEN 1 END) * 100.0 / 
                 NULLIF(COUNT(pp.cod_partida), 0)), 0
            ) * 0.4), 2
        ), 0
    ) as pontuacao_geral

FROM Atleta a
JOIN Equipe e ON a.cod_equipe = e.cod_equipe
LEFT JOIN Presenca_Treinamento pt ON a.id_atleta = pt.id_atleta
LEFT JOIN Presenca_Partida pp ON a.id_atleta = pp.id_atleta

GROUP BY a.id_atleta, a.nome_atleta, a.matricula_unb, a.curso, e.nome_equipe
-- Ordena por pontuação geral (maiores primeiro), depois por presença em treinamentos
ORDER BY pontuacao_geral DESC, percentual_presenca_treinamentos DESC, a.nome_atleta;