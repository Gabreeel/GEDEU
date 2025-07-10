-- ========================================
-- GEDEU 1.0 - SISTEMA DE GESTÃO DE EQUIPES DESPORTIVAS DA UnB
-- ========================================
-- Script completo para criação do banco de dados
-- Inclui: Tabelas, Dados de exemplo, Views e Procedures
-- Compatível com PostgreSQL 13+

-- Conectar ao banco (descomente se necessário)
-- \c GEDEU;

-- ========================================
-- CRIAÇÃO DAS TABELAS
-- ========================================

CREATE TABLE Modalidade (
    cod_modalidade SERIAL PRIMARY KEY,
    nome_modalidade VARCHAR(100) NOT NULL,
    desc_regras TEXT,
    categoria VARCHAR(20) CHECK (categoria IN ('Masculino', 'Feminino', 'Misto'))
);

CREATE TABLE Local (
    cod_local SERIAL PRIMARY KEY,
    endereco VARCHAR(255),
    nome_local VARCHAR(100),
    arquibancada BOOLEAN,
    coberto BOOLEAN
);

CREATE TABLE Evento (
    cod_evento SERIAL PRIMARY KEY,
    nome_evento VARCHAR(100) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    desc_evento TEXT,
    organizador_evento VARCHAR(100),
    cod_local INT,
    FOREIGN KEY (cod_local) REFERENCES Local(cod_local)
);

CREATE TABLE Campeonato (
    cod_campeonato SERIAL PRIMARY KEY,
    nome_campeonato VARCHAR(100) NOT NULL,
    ano_campeonato INT NOT NULL,
    desc_campeonato TEXT,
    organizador_campeonato VARCHAR(100),
    cod_modalidade INT,
    cod_evento INT,
    FOREIGN KEY (cod_modalidade) REFERENCES Modalidade(cod_modalidade),
    FOREIGN KEY (cod_evento) REFERENCES Evento(cod_evento)
);

CREATE TABLE Equipe (
    cod_equipe SERIAL PRIMARY KEY,
    nome_equipe VARCHAR(100) NOT NULL,
    ano_fundacao INT,
    status_ativa BOOLEAN
);

CREATE TABLE Participacao_Campeonato (
    cod_equipe INT,
    cod_campeonato INT,
    status_participacao VARCHAR(20),
    PRIMARY KEY (cod_equipe, cod_campeonato),
    FOREIGN KEY (cod_equipe) REFERENCES Equipe(cod_equipe),
    FOREIGN KEY (cod_campeonato) REFERENCES Campeonato(cod_campeonato)
);

CREATE TABLE Partida (
    cod_partida SERIAL PRIMARY KEY,
    data_partida DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    placar VARCHAR(20),
    cod_equipe_a INT,
    cod_equipe_b INT,
    cod_modalidade INT,
    cod_local INT,
    cod_evento INT,
    FOREIGN KEY (cod_equipe_a) REFERENCES Equipe(cod_equipe),
    FOREIGN KEY (cod_equipe_b) REFERENCES Equipe(cod_equipe),
    FOREIGN KEY (cod_modalidade) REFERENCES Modalidade(cod_modalidade),
    FOREIGN KEY (cod_local) REFERENCES Local(cod_local),
    FOREIGN KEY (cod_evento) REFERENCES Evento(cod_evento)
);

CREATE TABLE Documento (
    cod_documento SERIAL PRIMARY KEY,
    tipo_documento VARCHAR(50) NOT NULL,
    numero_documento VARCHAR(50) UNIQUE NOT NULL,
    arquivo_nome VARCHAR(255) NOT NULL, -- Nome original do arquivo
    arquivo_conteudo BYTEA NOT NULL, -- Conteúdo do PDF armazenado como BLOB
    arquivo_tamanho INTEGER, -- Tamanho do arquivo em bytes
    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Data de upload
);

CREATE TABLE Atleta (
    id_atleta SERIAL PRIMARY KEY,
    nome_atleta VARCHAR(100) NOT NULL,
    matricula_unb CHAR(9) NOT NULL CHECK (matricula_unb ~ '^[0-9]{9}$'),
    curso VARCHAR(100),
    email_atleta VARCHAR(100),
    telefone_atleta VARCHAR(20),
    data_nascimento DATE,
    status_ativo BOOLEAN,
    cod_equipe INT,
    cod_documento INT,
    FOREIGN KEY (cod_equipe) REFERENCES Equipe(cod_equipe),
    FOREIGN KEY (cod_documento) REFERENCES Documento(cod_documento)
);

CREATE TABLE Presenca_Partida (
    id_atleta INT,
    cod_partida INT,
    presenca BOOLEAN,
    obs TEXT,
    PRIMARY KEY (id_atleta, cod_partida),
    FOREIGN KEY (id_atleta) REFERENCES Atleta(id_atleta),
    FOREIGN KEY (cod_partida) REFERENCES Partida(cod_partida)
);

CREATE TABLE Treinador (
    id_treinador SERIAL PRIMARY KEY,
    nome_treinador VARCHAR(100) NOT NULL,
    email_treinador VARCHAR(100),
    telefone_treinador VARCHAR(20),
    status_ativo BOOLEAN,
    cod_documento INT,
    cod_equipe INT,
    FOREIGN KEY (cod_documento) REFERENCES Documento(cod_documento),
    FOREIGN KEY (cod_equipe) REFERENCES Equipe(cod_equipe)
);

CREATE TABLE Treinamento (
    cod_treinamento SERIAL PRIMARY KEY,
    data_treinamento DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_final TIME NOT NULL,
    cod_local INT,
    id_treinador INT,
    FOREIGN KEY (cod_local) REFERENCES Local(cod_local),
    FOREIGN KEY (id_treinador) REFERENCES Treinador(id_treinador)
);

CREATE TABLE Presenca_Treinamento (
    cod_treinamento INT,
    id_atleta INT,
    presenca BOOLEAN,
    obs TEXT,
    PRIMARY KEY (cod_treinamento, id_atleta),
    FOREIGN KEY (cod_treinamento) REFERENCES Treinamento(cod_treinamento),
    FOREIGN KEY (id_atleta) REFERENCES Atleta(id_atleta)
);