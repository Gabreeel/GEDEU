-- PROCEDURE 1: RELATORIO_PRESENCA_EQUIPE

-- Propósito: Gera um relatório completo de presença para uma equipe específica
--            incluindo dados de treinamentos e partidas
-- 
-- Como funciona:
-- - Recebe um código de equipe como parâmetro
-- - Busca todos os atletas da equipe
-- - Calcula estatísticas de presença em treinamentos e partidas
-- - Retorna dados agregados e individuais de cada atleta

CREATE OR REPLACE FUNCTION relatorio_presenca_equipe(equipe_id INTEGER)
RETURNS TABLE(
    id_atleta INTEGER,
    nome_atleta VARCHAR(100),
    total_treinamentos BIGINT,
    presencas_treinamentos BIGINT,
    percentual_treinamentos NUMERIC,
    total_partidas BIGINT,
    presencas_partidas BIGINT,
    percentual_partidas NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id_atleta,
        a.nome_atleta,
        
        -- Estatísticas de treinamentos
        COUNT(DISTINCT pt.cod_treinamento) as total_treinamentos,
        COUNT(CASE WHEN pt.presenca = true THEN 1 END) as presencas_treinamentos,
        COALESCE(
            ROUND(
                (COUNT(CASE WHEN pt.presenca = true THEN 1 END) * 100.0 / 
                 NULLIF(COUNT(pt.cod_treinamento), 0)), 2
            ), 0
        ) as percentual_treinamentos,
        
        -- Estatísticas de partidas
        COUNT(DISTINCT pp.cod_partida) as total_partidas,
        COUNT(CASE WHEN pp.presenca = true THEN 1 END) as presencas_partidas,
        COALESCE(
            ROUND(
                (COUNT(CASE WHEN pp.presenca = true THEN 1 END) * 100.0 / 
                 NULLIF(COUNT(pp.cod_partida), 0)), 2
            ), 0
        ) as percentual_partidas
        
    FROM Atleta a
    LEFT JOIN Presenca_Treinamento pt ON a.id_atleta = pt.id_atleta
    LEFT JOIN Presenca_Partida pp ON a.id_atleta = pp.id_atleta
    
    WHERE a.cod_equipe = equipe_id
    
    GROUP BY a.id_atleta, a.nome_atleta
    ORDER BY a.nome_atleta;
END;
$$ LANGUAGE plpgsql;

-- PROCEDURE 2: ESTATISTICAS_ATLETA

-- Propósito: Calcula estatísticas completas e detalhadas de um atleta específico
--            incluindo histórico de participações e performance
-- 
-- Como funciona:
-- - Recebe um ID de atleta como parâmetro
-- - Coleta dados de treinamentos, partidas e documentos
-- - Calcula médias, totais e percentuais de participação
-- - Retorna um registro completo com todas as estatísticas

CREATE OR REPLACE FUNCTION estatisticas_atleta(atleta_id INTEGER)
RETURNS TABLE(
    id_atleta INTEGER,
    nome_atleta VARCHAR(100),
    matricula_unb CHAR(9),
    curso VARCHAR(100),
    nome_equipe VARCHAR(100),
    data_nascimento DATE,
    idade INTEGER,
    total_treinamentos_convocado BIGINT,
    total_presencas_treinamentos BIGINT,
    percentual_presenca_treinamentos NUMERIC,
    total_partidas_convocado BIGINT,
    total_presencas_partidas BIGINT,
    percentual_presenca_partidas NUMERIC,
    total_faltas_treinamentos BIGINT,
    total_faltas_partidas BIGINT,
    pontuacao_geral NUMERIC,
    status_participacao VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id_atleta,
        a.nome_atleta,
        a.matricula_unb,
        a.curso,
        e.nome_equipe,
        a.data_nascimento,
        
        -- Cálculo da idade
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, a.data_nascimento))::INTEGER as idade,
        
        -- Estatísticas de treinamentos
        COUNT(DISTINCT pt.cod_treinamento) as total_treinamentos_convocado,
        COUNT(CASE WHEN pt.presenca = true THEN 1 END) as total_presencas_treinamentos,
        COALESCE(
            ROUND(
                (COUNT(CASE WHEN pt.presenca = true THEN 1 END) * 100.0 / 
                 NULLIF(COUNT(pt.cod_treinamento), 0)), 2
            ), 0
        ) as percentual_presenca_treinamentos,
        
        -- Estatísticas de partidas
        COUNT(DISTINCT pp.cod_partida) as total_partidas_convocado,
        COUNT(CASE WHEN pp.presenca = true THEN 1 END) as total_presencas_partidas,
        COALESCE(
            ROUND(
                (COUNT(CASE WHEN pp.presenca = true THEN 1 END) * 100.0 / 
                 NULLIF(COUNT(pp.cod_partida), 0)), 2
            ), 0
        ) as percentual_presenca_partidas,
        
        -- Contagem de faltas
        COUNT(CASE WHEN pt.presenca = false THEN 1 END) as total_faltas_treinamentos,
        COUNT(CASE WHEN pp.presenca = false THEN 1 END) as total_faltas_partidas,
        
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
        ) as pontuacao_geral,
        
        -- Status de participação baseado na pontuação
        CASE 
            WHEN COALESCE(
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
            ) >= 90 THEN 'Excelente'
            WHEN COALESCE(
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
            ) >= 80 THEN 'Ótimo'
            WHEN COALESCE(
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
            ) >= 70 THEN 'Bom'
            WHEN COALESCE(
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
            ) >= 60 THEN 'Regular'
            ELSE 'Needs Improvement'
        END as status_participacao
        
    FROM Atleta a
    JOIN Equipe e ON a.cod_equipe = e.cod_equipe
    LEFT JOIN Presenca_Treinamento pt ON a.id_atleta = pt.id_atleta
    LEFT JOIN Presenca_Partida pp ON a.id_atleta = pp.id_atleta
    
    WHERE a.id_atleta = atleta_id
    
    GROUP BY a.id_atleta, a.nome_atleta, a.matricula_unb, a.curso, 
             e.nome_equipe, a.data_nascimento;
END;
$$ LANGUAGE plpgsql;