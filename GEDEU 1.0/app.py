from flask import Flask, render_template, request, redirect, url_for, send_file, Response
import psycopg2
from werkzeug.utils import secure_filename
import os
import re
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def get_db_connection():
    return psycopg2.connect(
        database="GEDEU",
        host="localhost",
        user="seu_usuario_aqui",
        password="sua_senha_aqui",
        port="5432"
    )

TABLES = [
    "Modalidade", "Local", "Evento", "Campeonato", "Equipe",
    "Participacao_Campeonato", "Partida", "Atleta", "Documento",
    "Presenca_Partida", "Treinador", "Treinamento", "Presenca_Treinamento"
]

# Views do sistema
VIEWS = [
    "dashboard_equipes", "ranking_atletas"
]

DISPLAY_NAMES = {
    "Modalidade": "Modalidades",
    "Local": "Locais",
    "Evento": "Eventos",
    "Campeonato": "Campeonatos",
    "Equipe": "Equipes",
    "Participacao_Campeonato": "Participações em Campeonatos",
    "Partida": "Partidas",
    "Atleta": "Atletas",
    "Documento": "Documentos",
    "Presenca_Partida": "Presenças em Partidas",
    "Treinador": "Treinadores",
    "Treinamento": "Treinamentos",
    "Presenca_Treinamento": "Presenças em Treinamentos",
    # Views
    "dashboard_equipes": "Dashboard de Equipes",
    "ranking_atletas": "Ranking de Atletas"
}

COLUMN_DISPLAY_NAMES = {
    "Modalidade": {
        "cod_modalidade": "Código",
        "nome_modalidade": "Nome da Modalidade",
        "desc_regras": "Descrição das Regras",
        "categoria": "Categoria"
    },
    "Local": {
        "cod_local": "Código",
        "endereco": "Endereço",
        "nome_local": "Nome do Local",
        "arquibancada": "Arquibancada",
        "coberto": "Coberto"
    },
    "Evento": {
        "cod_evento": "Código",
        "nome_evento": "Nome do Evento",
        "data_inicio": "Data de Início",
        "data_fim": "Data de Fim",
        "desc_evento": "Descrição",
        "organizador_evento": "Organizador",
        "cod_local": "Código do Local"
    },
    "Campeonato": {
        "cod_campeonato": "Código",
        "nome_campeonato": "Nome do Campeonato",
        "ano_campeonato": "Ano",
        "desc_campeonato": "Descrição",
        "organizador_campeonato": "Organizador",
        "cod_modalidade": "Código da Modalidade",
        "cod_evento": "Código do Evento"
    },
    "Equipe": {
        "cod_equipe": "Código",
        "nome_equipe": "Nome da Equipe",
        "ano_fundacao": "Ano de Fundação",
        "status_ativa": "Status"
    },
    "Participacao_Campeonato": {
        "cod_equipe": "Código da Equipe",
        "cod_campeonato": "Código do Campeonato",
        "status_participacao": "Status da Participação"
    },
    "Partida": {
        "cod_partida": "Código",
        "data_partida": "Data da Partida",
        "hora_inicio": "Hora de Início",
        "placar": "Placar",
        "cod_equipe_a": "Equipe A",
        "cod_equipe_b": "Equipe B",
        "cod_modalidade": "Modalidade",
        "cod_local": "Local",
        "cod_evento": "Evento"
    },
    "Atleta": {
        "id_atleta": "Código",
        "nome_atleta": "Nome do Atleta",
        "matricula_unb": "Matrícula UnB",
        "curso": "Curso",
        "email_atleta": "E-mail",
        "telefone_atleta": "Telefone",
        "data_nascimento": "Data de Nascimento",
        "status_ativo": "Status",
        "cod_equipe": "Equipe",
        "cod_documento": "Documento"
    },
    "Documento": {
        "cod_documento": "Código",
        "tipo_documento": "Tipo de Documento",
        "numero_documento": "Número do Documento",
        "arquivo_nome": "Nome do Arquivo",
        "arquivo_tamanho": "Tamanho (bytes)",
        "data_upload": "Data de Upload"
    },
    "Presenca_Partida": {
        "id_atleta": "Atleta",
        "cod_partida": "Partida",
        "presenca": "Presença",
        "obs": "Observação"
    },
    "Treinador": {
        "id_treinador": "Código",
        "nome_treinador": "Nome do Treinador",
        "email_treinador": "E-mail",
        "telefone_treinador": "Telefone",
        "status_ativo": "Status",
        "cod_documento": "Documento",
        "cod_equipe": "Equipe"
    },
    "Treinamento": {
        "cod_treinamento": "Código",
        "data_treinamento": "Data do Treinamento",
        "hora_inicio": "Hora de Início",
        "hora_final": "Hora Final",
        "cod_local": "Local",
        "id_treinador": "Treinador"
    },
    "Presenca_Treinamento": {
        "cod_treinamento": "Treinamento",
        "id_atleta": "Atleta",
        "presenca": "Presença",
        "obs": "Observação"
    }
}

# Mapeamento de FK: coluna -> (tabela referenciada, coluna PK, coluna nome amigável)
FK_FIELDS = {
    "Atleta": {
        "cod_equipe": ("Equipe", "cod_equipe", "nome_equipe"),
        "cod_documento": ("Documento", "cod_documento", "numero_documento")
    },
    "Evento": {
        "cod_local": ("Local", "cod_local", "nome_local")
    },
    "Campeonato": {
        "cod_modalidade": ("Modalidade", "cod_modalidade", "nome_modalidade"),
        "cod_evento": ("Evento", "cod_evento", "nome_evento")
    },
    "Partida": {
        "cod_equipe_a": ("Equipe", "cod_equipe", "nome_equipe"),
        "cod_equipe_b": ("Equipe", "cod_equipe", "nome_equipe"),
        "cod_modalidade": ("Modalidade", "cod_modalidade", "nome_modalidade"),
        "cod_local": ("Local", "cod_local", "nome_local"),
        "cod_evento": ("Evento", "cod_evento", "nome_evento")
    },
    "Treinador": {
        "cod_documento": ("Documento", "cod_documento", "numero_documento"),
        "cod_equipe": ("Equipe", "cod_equipe", "nome_equipe")
    },
    "Treinamento": {
        "cod_local": ("Local", "cod_local", "nome_local"),
        "id_treinador": ("Treinador", "id_treinador", "nome_treinador")
    },
    "Presenca_Partida": {
        "id_atleta": ("Atleta", "id_atleta", "nome_atleta"),
        "cod_partida": ("Partida", "cod_partida", "cod_partida")
    },
    "Presenca_Treinamento": {
        "cod_treinamento": ("Treinamento", "cod_treinamento", "cod_treinamento"),
        "id_atleta": ("Atleta", "id_atleta", "nome_atleta")
    },
    "Participacao_Campeonato": {
        "cod_equipe": ("Equipe", "cod_equipe", "nome_equipe"),
        "cod_campeonato": ("Campeonato", "cod_campeonato", "nome_campeonato")
    }
}

def get_fk_options(table):
    options = {}
    if table in FK_FIELDS:
        conn = get_db_connection()
        cur = conn.cursor()
        for col, (ref_table, pk_col, name_col) in FK_FIELDS[table].items():
            try:
                cur.execute(f"SELECT {pk_col}, {name_col} FROM {ref_table}")
                options[col] = cur.fetchall()
            except Exception:
                options[col] = []
        cur.close()
        conn.close()
    return options

@app.route('/')
def index():
    tables = [t for t in TABLES if t not in ["Participacao_Campeonato", "Presenca_Partida"]]
    return render_template('index.html', tables=tables, display_names=DISPLAY_NAMES)

@app.route('/<table>')
def show_table(table):
    if table not in TABLES:
        return "Tabela não encontrada", 404
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Construir query com filtros para Atleta e Treinador
    query = f"SELECT * FROM {table}"
    params = []
    filters = []
    
    # Filtros específicos para Atleta e Treinador
    if table in ['Atleta', 'Treinador']:
        status_filter = request.args.get('status')
        equipe_filter = request.args.get('equipe')
        
        if status_filter:
            if status_filter == 'ativo':
                filters.append("status_ativo = TRUE")
            elif status_filter == 'inativo':
                filters.append("status_ativo = FALSE")
        
        if equipe_filter:
            filters.append("cod_equipe = %s")
            params.append(equipe_filter)
        
        if filters:
            query += " WHERE " + " AND ".join(filters)
    
    if params:
        cur.execute(query, params)
    else:
        cur.execute(query)
    
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    equipe_nomes = {}
    if any(col in colnames for col in ['cod_equipe', 'cod_equipe_a', 'cod_equipe_b']):
        cur.execute("SELECT cod_equipe, nome_equipe FROM Equipe")
        equipe_nomes = {row[0]: row[1] for row in cur.fetchall()}
    documento_infos = {}
    if 'cod_documento' in colnames:
        cur.execute("SELECT cod_documento, tipo_documento, numero_documento FROM Documento")
        documento_infos = {row[0]: {'tipo': row[1], 'numero': row[2]} for row in cur.fetchall()}
    local_nomes = {}
    treinador_nomes = {}
    modalidade_nomes = {}
    evento_nomes = {}
    if table in ["Treinamento", "Evento", "Campeonato", "Partida"]:
        cur.execute("SELECT cod_local, nome_local FROM Local")
        local_nomes = {row[0]: row[1] for row in cur.fetchall()}
    if table == "Treinamento":
        cur.execute("SELECT id_treinador, nome_treinador FROM Treinador")
        treinador_nomes = {row[0]: row[1] for row in cur.fetchall()}
    if table in ["Campeonato", "Partida"]:
        cur.execute("SELECT cod_modalidade, nome_modalidade FROM Modalidade")
        modalidade_nomes = {row[0]: row[1] for row in cur.fetchall()}
    if table in ["Campeonato", "Partida"]:
        cur.execute("SELECT cod_evento, nome_evento FROM Evento")
        evento_nomes = {row[0]: row[1] for row in cur.fetchall()}
    cur.close()
    conn.close()
    display_colnames = [COLUMN_DISPLAY_NAMES.get(table, {}).get(col, col) for col in colnames]
    
    # Formatar dados BLOB para exibição amigável
    rows = format_blob_data(rows, colnames, table)
    
    # Buscar equipes disponíveis para filtro (apenas para Atleta e Treinador)
    equipes_filtro = []
    if table in ['Atleta', 'Treinador']:
        conn2 = get_db_connection()
        cur2 = conn2.cursor()
        cur2.execute("SELECT cod_equipe, nome_equipe FROM Equipe ORDER BY nome_equipe")
        equipes_filtro = cur2.fetchall()
        cur2.close()
        conn2.close()
    
    return render_template(
        'table.html',
        table=table,
        rows=rows,
        colnames=colnames,
        display_colnames=display_colnames,
        display_names=DISPLAY_NAMES,
        equipe_nomes=equipe_nomes,
        documento_infos=documento_infos,
        local_nomes=local_nomes,
        treinador_nomes=treinador_nomes,
        modalidade_nomes=modalidade_nomes,
        evento_nomes=evento_nomes,
        equipes_filtro=equipes_filtro,
        status_filter=request.args.get('status'),
        equipe_filter=request.args.get('equipe')
    )

@app.route('/participantes_campeonato/<cod_campeonato>', methods=['GET', 'POST'])
def participantes_campeonato(cod_campeonato):
    conn = get_db_connection()
    cur = conn.cursor()
    # Buscar nome do campeonato
    cur.execute("SELECT nome_campeonato FROM Campeonato WHERE cod_campeonato = %s", (cod_campeonato,))
    nome_campeonato = cur.fetchone()
    # Buscar equipes já participantes
    cur.execute("""
        SELECT pc.cod_equipe, e.nome_equipe, pc.status_participacao
        FROM Participacao_Campeonato pc
        JOIN Equipe e ON pc.cod_equipe = e.cod_equipe
        WHERE pc.cod_campeonato = %s
    """, (cod_campeonato,))
    participantes = cur.fetchall()
    # Buscar equipes que ainda não participam deste campeonato
    cur.execute("""
        SELECT cod_equipe, nome_equipe FROM Equipe
        WHERE cod_equipe NOT IN (
            SELECT cod_equipe FROM Participacao_Campeonato WHERE cod_campeonato = %s
        )
    """, (cod_campeonato,))
    equipes_disponiveis = cur.fetchall()
    if request.method == 'POST':
        cod_equipe = request.form.get('cod_equipe')
        status_participacao = request.form.get('status_participacao')
        if cod_equipe and status_participacao:
            cur.execute("""
                INSERT INTO Participacao_Campeonato (cod_equipe, cod_campeonato, status_participacao)
                VALUES (%s, %s, %s)
            """, (cod_equipe, cod_campeonato, status_participacao))
            conn.commit()
        return redirect(url_for('participantes_campeonato', cod_campeonato=cod_campeonato))
    cur.close()
    conn.close()
    return render_template(
        'participantes_campeonato.html',
        cod_campeonato=cod_campeonato,
        nome_campeonato=nome_campeonato[0] if nome_campeonato else '',
        participantes=participantes,
        equipes_disponiveis=equipes_disponiveis
    )

@app.route('/<table>/add', methods=['GET', 'POST'])
def add_row(table):
    if table not in TABLES:
        return "Tabela não encontrada", 404
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} LIMIT 0")
    colnames = [desc[0] for desc in cur.description]
    insert_cols = colnames[1:]
    fk_options = get_fk_options(table)
    doc_fields = []
    if table in ['Atleta', 'Treinador']:
        doc_fields = ['tipo_documento', 'numero_documento', 'arquivo']
    if request.method == 'POST':
        values = []
        doc_cod = None
        if table in ['Atleta', 'Treinador']:
            tipo_documento = request.form.get('tipo_documento')
            numero_documento = request.form.get('numero_documento')
            file = request.files.get('arquivo')
            if not file or file.filename == '' or not allowed_file(file.filename):
                return "Por favor, envie um arquivo PDF válido.", 400
            
            # Lê o conteúdo do arquivo para armazenar como BLOB
            file_content = file.read()
            filename = secure_filename(file.filename)
            file_size = len(file_content)
            
            # Verifica unicidade do número do documento antes de inserir
            conn2 = get_db_connection()
            cur2 = conn2.cursor()
            cur2.execute("SELECT 1 FROM Documento WHERE numero_documento = %s", (numero_documento,))
            if cur2.fetchone():
                cur2.close()
                conn2.close()
                return "Já existe um documento cadastrado com este número.", 400
            cur2.execute(
                "INSERT INTO Documento (tipo_documento, numero_documento, arquivo_nome, arquivo_conteudo, arquivo_tamanho) VALUES (%s, %s, %s, %s, %s) RETURNING cod_documento",
                (tipo_documento, numero_documento, filename, file_content, file_size)
            )
            doc_cod = cur2.fetchone()[0]
            conn2.commit()
            cur2.close()
            conn2.close()
        for col in insert_cols:
            if col.startswith('status_'):
                values.append(request.form.get(col) == 'on')
            elif col == 'matricula_unb':
                matricula = request.form.get(col)
                if not matricula or not re.fullmatch(r'\d{9}', matricula):
                    return "Matrícula deve conter exatamente 9 números.", 400
                values.append(matricula)
            elif col in ['email_atleta', 'email_treinador']:
                email = request.form.get(col)
                if not email or not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
                    return "E-mail inválido.", 400
                values.append(email)
            elif col in ['telefone_atleta', 'telefone_treinador']:
                telefone = request.form.get(col)
                if not telefone or not re.fullmatch(r'\d{11}', telefone):
                    return "Telefone deve conter exatamente 11 números.", 400
                values.append(telefone)
            elif col == 'cod_documento' and table in ['Atleta', 'Treinador']:
                values.append(doc_cod)
            elif table in FK_FIELDS and col in fk_options:
                values.append(request.form.get(col))
            else:
                values.append(request.form.get(col))
        placeholders = ','.join(['%s'] * len(values))
        cur.execute(
            f"INSERT INTO {table} ({','.join(insert_cols)}) VALUES ({placeholders})",
            values
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('show_table', table=table))
    cur.close()
    conn.close()
    return render_template(
        'add_edit.html',
        table=table,
        colnames=insert_cols,
        row=None,
        current_values={},
        COLUMN_DISPLAY_NAMES=COLUMN_DISPLAY_NAMES,
        fk_options=fk_options,
        doc_fields=doc_fields
    )

@app.route('/<table>/edit/<pk>', methods=['GET', 'POST'])
def edit_row(table, pk):
    if table not in TABLES:
        return "Tabela não encontrada", 404
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} LIMIT 0")
    colnames = [desc[0] for desc in cur.description]
    pk_col = colnames[0]
    cur.execute(f"SELECT * FROM {table} WHERE {pk_col} = %s", (pk,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return "Registro não encontrado", 404
    edit_cols = colnames[1:]
    fk_options = get_fk_options(table)  # <-- Certifique-se de definir fk_options antes do bloco POST
    doc_fields = []
    doc_row = None
    if table in ['Atleta', 'Treinador']:
        # Busca dados do documento relacionado
        idx_cod_doc = edit_cols.index('cod_documento')
        cod_doc = row[idx_cod_doc+1]
        conn2 = get_db_connection()
        cur2 = conn2.cursor()
        cur2.execute("SELECT tipo_documento, numero_documento, arquivo FROM Documento WHERE cod_documento = %s", (cod_doc,))
        doc_row = cur2.fetchone()
        cur2.close()
        conn2.close()
        doc_fields = ['tipo_documento', 'numero_documento', 'arquivo']
    
    # Criar um dicionário com os valores atuais para facilitar o acesso no template
    current_values = {}
    if row:
        for i, col in enumerate(edit_cols):
            current_values[col] = row[i + 1]  # row[i + 1] porque row[0] é a chave primária
    
    if request.method == 'POST':
        values = []
        # Atualiza documento se for Atleta/Treinador
        if table in ['Atleta', 'Treinador']:
            tipo_documento = request.form.get('tipo_documento')
            numero_documento = request.form.get('numero_documento')
            file = request.files.get('arquivo')
            idx_cod_doc = edit_cols.index('cod_documento')
            cod_doc = row[idx_cod_doc+1]
            conn2 = get_db_connection()
            cur2 = conn2.cursor()
            if file and file.filename != '':
                if not allowed_file(file.filename):
                    cur2.close()
                    conn2.close()
                    return "Por favor, envie um arquivo PDF válido.", 400
                
                # Lê o conteúdo do arquivo para armazenar como BLOB
                file_content = file.read()
                filename = secure_filename(file.filename)
                file_size = len(file_content)
                
                cur2.execute(
                    "UPDATE Documento SET tipo_documento=%s, numero_documento=%s, arquivo_nome=%s, arquivo_conteudo=%s, arquivo_tamanho=%s WHERE cod_documento=%s",
                    (tipo_documento, numero_documento, filename, file_content, file_size, cod_doc)
                )
            else:
                cur2.execute(
                    "UPDATE Documento SET tipo_documento=%s, numero_documento=%s WHERE cod_documento=%s",
                    (tipo_documento, numero_documento, cod_doc)
                )
            conn2.commit()
            cur2.close()
            conn2.close()
        for idx, col in enumerate(edit_cols):
            if col.startswith('status_'):
                values.append(request.form.get(col) == 'on')
            elif col == 'matricula_unb':
                matricula = request.form.get(col)
                if not matricula or not re.fullmatch(r'\d{9}', matricula):
                    return "Matrícula deve conter exatamente 9 números.", 400
                values.append(matricula)
            elif col in ['email_atleta', 'email_treinador']:
                email = request.form.get(col)
                if not email or not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
                    return "E-mail inválido.", 400
                values.append(email)
            elif col in ['telefone_atleta', 'telefone_treinador']:
                telefone = request.form.get(col)
                if not telefone or not re.fullmatch(r'\d{11}', telefone):
                    return "Telefone deve conter exatamente 11 números.", 400
                values.append(telefone)
            elif col == 'cod_documento' and table in ['Atleta', 'Treinador']:
                # Para Atleta/Treinador, o cod_documento não deve ser alterado
                # pois é gerenciado pelos campos de documento separados
                values.append(current_values[col] if current_values and col in current_values else row[idx + 1])
            elif table in FK_FIELDS and col in fk_options:
                values.append(request.form.get(col))
            else:
                values.append(request.form.get(col))
        set_clause = ','.join([f"{col}=%s" for col in edit_cols])
        cur.execute(
            f"UPDATE {table} SET {set_clause} WHERE {pk_col} = %s",
            values + [pk]
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('show_table', table=table))
    cur.close()
    conn.close()
    
    return render_template(
        'add_edit.html',
        table=table,
        colnames=edit_cols,
        row=row[1:] if row else None,
        current_values=current_values,
        COLUMN_DISPLAY_NAMES=COLUMN_DISPLAY_NAMES,
        fk_options=fk_options,
        doc_fields=doc_fields,
        doc_row=doc_row
    )

@app.route('/edit_document/<table>/<pk>', methods=['GET', 'POST'])
def edit_document(table, pk):
    # Busca cod_documento
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT cod_documento FROM {table} WHERE {('id_atleta' if table=='Atleta' else 'id_treinador')} = %s", (pk,))
    cod_doc = cur.fetchone()
    if not cod_doc:
        cur.close()
        conn.close()
        return "Documento não encontrado", 404
    cod_doc = cod_doc[0]
    cur.execute("SELECT tipo_documento, numero_documento, arquivo FROM Documento WHERE cod_documento = %s", (cod_doc,))
    doc_row = cur.fetchone()
    cur.close()
    conn.close()
    if request.method == 'POST':
        tipo_documento = request.form.get('tipo_documento')
        numero_documento = request.form.get('numero_documento')
        file = request.files.get('arquivo')
        conn2 = get_db_connection()
        cur2 = conn2.cursor()
        if file and file.filename != '':
            if not allowed_file(file.filename):
                cur2.close()
                conn2.close()
                return "Por favor, envie um arquivo PDF válido.", 400
            
            # Lê o conteúdo do arquivo para armazenar como BLOB
            file_content = file.read()
            filename = secure_filename(file.filename)
            file_size = len(file_content)
            
            cur2.execute(
                "UPDATE Documento SET tipo_documento=%s, numero_documento=%s, arquivo_nome=%s, arquivo_conteudo=%s, arquivo_tamanho=%s WHERE cod_documento=%s",
                (tipo_documento, numero_documento, filename, file_content, file_size, cod_doc)
            )
        else:
            cur2.execute(
                "UPDATE Documento SET tipo_documento=%s, numero_documento=%s WHERE cod_documento=%s",
                (tipo_documento, numero_documento, cod_doc)
            )
        conn2.commit()
        cur2.close()
        conn2.close()
        return redirect(url_for('show_table', table=table))
    return render_template(
        'edit_document.html',
        table=table,
        pk=pk,
        doc_row=doc_row
    )

# Rota para servir arquivos PDF
@app.route('/documento/<int:cod_documento>')
def ver_documento(cod_documento):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT arquivo, tipo_documento, numero_documento FROM Documento WHERE cod_documento = %s", (cod_documento,))
    doc = cur.fetchone()
    cur.close()
    conn.close()
    
    if not doc:
        return "Documento não encontrado", 404
    
    arquivo_path, tipo_doc, numero_doc = doc
    
    # Verificar se o arquivo existe fisicamente
    if not os.path.exists(arquivo_path):
        return f"Arquivo PDF não encontrado no sistema de arquivos: {arquivo_path}", 404
    
    try:
        return send_file(arquivo_path, as_attachment=False, download_name=f"{tipo_doc}_{numero_doc}.pdf")
    except Exception as e:
        return f"Erro ao abrir o arquivo: {str(e)}", 500

@app.route('/download_pdf/<int:cod_documento>')
def download_pdf(cod_documento):
    """Serve um PDF armazenado como BLOB no banco de dados"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT arquivo_nome, arquivo_conteudo FROM Documento WHERE cod_documento = %s",
            (cod_documento,)
        )
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if not result:
            return "Documento não encontrado", 404
        
        filename, file_content = result
        
        # Cria um objeto de arquivo em memória
        file_obj = io.BytesIO(file_content)
        
        return Response(
            file_obj.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'inline; filename="{filename}"',
                'Content-Type': 'application/pdf'
            }
        )
        
    except Exception as e:
        return f"Erro ao baixar documento: {str(e)}", 500

@app.template_filter('basename')
def basename_filter(path):
    return os.path.basename(path) if path else ''

@app.template_filter('telefone_format')
def telefone_format_filter(value):
    if not value or len(value) != 11 or not value.isdigit():
        return value
    return f"({value[:2]}) {value[2:7]}-{value[7:]}"

@app.route('/presenca_treinamento/<cod_treinamento>', methods=['GET', 'POST'])
def presenca_treinamento(cod_treinamento):
    conn = get_db_connection()
    cur = conn.cursor()
    # Buscar dados do treinamento, treinador e equipe do treinador
    cur.execute("""
        SELECT t.data_treinamento, t.hora_inicio, t.hora_final, tr.nome_treinador, tr.cod_equipe
        FROM Treinamento t
        JOIN Treinador tr ON t.id_treinador = tr.id_treinador
        WHERE t.cod_treinamento = %s
    """, (cod_treinamento,))
    treino_info = cur.fetchone()
    if not treino_info:
        cur.close()
        conn.close()
        return "Treinamento não encontrado", 404
    data_treinamento, hora_inicio, hora_final, nome_treinador, cod_equipe = treino_info

    # Buscar atletas da mesma equipe do treinador
    cur.execute("""
        SELECT id_atleta, nome_atleta FROM Atleta
        WHERE cod_equipe = %s
    """, (cod_equipe,))
    atletas_equipe = cur.fetchall()

    # Adicionar presença se POST
    if request.method == 'POST':
        id_atleta = request.form.get('id_atleta')
        presenca = request.form.get('presenca') == 'on'
        obs = request.form.get('obs')
        # Verifica se já existe presença para esse atleta/treinamento
        cur.execute("""
            SELECT 1 FROM Presenca_Treinamento WHERE cod_treinamento = %s AND id_atleta = %s
        """, (cod_treinamento, id_atleta))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO Presenca_Treinamento (cod_treinamento, id_atleta, presenca, obs)
                VALUES (%s, %s, %s, %s)
            """, (cod_treinamento, id_atleta, presenca, obs))
            conn.commit()

    # Buscar presenças já cadastradas
    cur.execute("""
        SELECT pt.id_atleta, a.nome_atleta, pt.presenca, pt.obs
        FROM Presenca_Treinamento pt
        JOIN Atleta a ON pt.id_atleta = a.id_atleta
        WHERE pt.cod_treinamento = %s
    """, (cod_treinamento,))
    presencas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template(
        'presenca_treinamento.html',
        cod_treinamento=cod_treinamento,
        presencas=presencas,
        atletas_equipe=atletas_equipe,
        nome_treinador=nome_treinador,
        data_treinamento=data_treinamento,
        hora_inicio=hora_inicio,
        hora_final=hora_final
    )

@app.route('/presenca_partida/<cod_partida>', methods=['GET', 'POST'])
def presenca_partida(cod_partida):
    conn = get_db_connection()
    cur = conn.cursor()
    # Buscar dados da partida (equipes participantes)
    cur.execute("""
        SELECT cod_equipe_a, cod_equipe_b FROM Partida WHERE cod_partida = %s
    """, (cod_partida,))
    partida = cur.fetchone()
    if not partida:
        cur.close()
        conn.close()
        return "Partida não encontrada", 404
    cod_equipe_a, cod_equipe_b = partida

    # Buscar atletas das equipes participantes
    cur.execute("""
        SELECT id_atleta, nome_atleta, cod_equipe FROM Atleta
        WHERE cod_equipe IN (%s, %s)
    """, (cod_equipe_a, cod_equipe_b))
    atletas = cur.fetchall()

    # Buscar nomes das equipes
    cur.execute("SELECT cod_equipe, nome_equipe FROM Equipe WHERE cod_equipe IN (%s, %s)", (cod_equipe_a, cod_equipe_b))
    equipe_nomes = {row[0]: row[1] for row in cur.fetchall()}

    # Adicionar presença se POST
    if request.method == 'POST':
        id_atleta = request.form.get('id_atleta')
        presenca = request.form.get('presenca') == 'on'
        obs = request.form.get('obs')
        # Verifica se já existe presença para esse atleta/partida
        cur.execute("""
            SELECT 1 FROM Presenca_Partida WHERE cod_partida = %s AND id_atleta = %s
        """, (cod_partida, id_atleta))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO Presenca_Partida (id_atleta, cod_partida, presenca, obs)
                VALUES (%s, %s, %s, %s)
            """, (id_atleta, cod_partida, presenca, obs))
            conn.commit()

    # Buscar presenças já cadastradas
    cur.execute("""
        SELECT pp.id_atleta, a.nome_atleta, a.cod_equipe, pp.presenca, pp.obs
        FROM Presenca_Partida pp
        JOIN Atleta a ON pp.id_atleta = a.id_atleta
        WHERE pp.cod_partida = %s
    """, (cod_partida,))
    presencas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template(
        'presenca_partida.html',
        cod_partida=cod_partida,
        presencas=presencas,
        atletas=atletas,
        equipe_nomes=equipe_nomes
    )

@app.route('/relatorio_presenca_equipe', methods=['GET', 'POST'])
def relatorio_presenca_equipe():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Buscar todas as equipes para o dropdown
    cur.execute("SELECT cod_equipe, nome_equipe FROM Equipe ORDER BY nome_equipe")
    equipes = cur.fetchall()
    
    relatorio_data = []
    equipe_selecionada = None
    data_inicio = None
    data_fim = None
    
    if request.method == 'POST':
        cod_equipe = request.form.get('cod_equipe')
        data_inicio = request.form.get('data_inicio') or None
        data_fim = request.form.get('data_fim') or None
        
        if cod_equipe:
            equipe_selecionada = cod_equipe
            # Chamar a procedure com conversão explícita de tipos
            if data_inicio and data_fim:
                cur.execute("SELECT * FROM relatorio_presenca_equipe(%s::INTEGER, %s::DATE, %s::DATE)", 
                           (cod_equipe, data_inicio, data_fim))
            elif data_inicio:
                cur.execute("SELECT * FROM relatorio_presenca_equipe(%s::INTEGER, %s::DATE, NULL)", 
                           (cod_equipe, data_inicio))
            elif data_fim:
                cur.execute("SELECT * FROM relatorio_presenca_equipe(%s::INTEGER, NULL, %s::DATE)", 
                           (cod_equipe, data_fim))
            else:
                cur.execute("SELECT * FROM relatorio_presenca_equipe(%s::INTEGER)", (cod_equipe,))
            
            relatorio_data = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('relatorio_presenca_equipe.html', 
                         equipes=equipes, 
                         relatorio_data=relatorio_data,
                         equipe_selecionada=equipe_selecionada,
                         data_inicio=data_inicio,
                         data_fim=data_fim)

@app.route('/estatisticas_atleta', methods=['GET', 'POST'])
def estatisticas_atleta():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Buscar todos os atletas para o dropdown
    cur.execute("SELECT id_atleta, nome_atleta FROM Atleta WHERE status_ativo = TRUE ORDER BY nome_atleta")
    atletas = cur.fetchall()
    
    estatisticas = None
    atleta_selecionado = None
    
    if request.method == 'POST':
        id_atleta = request.form.get('id_atleta')
        
        if id_atleta:
            atleta_selecionado = id_atleta
            # Chamar a procedure com conversão explícita de tipo
            cur.execute("SELECT * FROM estatisticas_atleta(%s::INTEGER)", (id_atleta,))
            estatisticas = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return render_template('estatisticas_atleta.html', 
                         atletas=atletas, 
                         estatisticas=estatisticas,
                         atleta_selecionado=atleta_selecionado)

@app.route('/view/<view_name>')
def show_view(view_name):
    if view_name not in VIEWS:
        return "View não encontrada", 404
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {view_name}")
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    
    return render_template('view_table.html', 
                         view_name=view_name,
                         rows=rows, 
                         colnames=colnames,
                         display_name=DISPLAY_NAMES.get(view_name, view_name))

def format_blob_data(rows, colnames, table):
    """Formata dados BLOB para exibição mais amigável"""
    if table != 'Documento':
        return rows
    
    # Encontrar índice da coluna arquivo_conteudo
    blob_col_index = None
    try:
        blob_col_index = colnames.index('arquivo_conteudo')
    except ValueError:
        return rows  # Coluna não existe
    
    # Processar cada linha
    formatted_rows = []
    for row in rows:
        row_list = list(row)
        
        # Formatar coluna BLOB
        if blob_col_index < len(row_list) and row_list[blob_col_index] is not None:
            blob_data = row_list[blob_col_index]
            # Converter para indicador amigável
            if isinstance(blob_data, (bytes, memoryview)):
                size = len(blob_data)
                row_list[blob_col_index] = f"BLOB ({size:,} bytes)"
            else:
                row_list[blob_col_index] = "BLOB (dados binários)"
        
        formatted_rows.append(tuple(row_list))
    
    return formatted_rows

@app.route('/<table>/delete/<pk>', methods=['POST'])
def delete_record(table, pk):
    """Deleta um registro de uma tabela específica"""
    if table not in TABLES:
        return "Tabela não encontrada", 404
    
    # Mapeamento das chaves primárias para cada tabela
    primary_keys = {
        "Modalidade": "cod_modalidade",
        "Local": "cod_local", 
        "Evento": "cod_evento",
        "Campeonato": "cod_campeonato",
        "Equipe": "cod_equipe",
        "Partida": "cod_partida",
        "Atleta": "id_atleta",
        "Documento": "cod_documento",
        "Treinador": "id_treinador",
        "Treinamento": "cod_treinamento"
    }
    
    # Mapeamento para tabelas com chaves compostas
    composite_keys = {
        "Participacao_Campeonato": ["cod_equipe", "cod_campeonato"],
        "Presenca_Partida": ["id_atleta", "cod_partida"],
        "Presenca_Treinamento": ["cod_treinamento", "id_atleta"]
    }
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if table in composite_keys:
            # Para chaves compostas, pk deve ser no formato "valor1_valor2"
            pk_values = pk.split('_')
            if len(pk_values) != len(composite_keys[table]):
                return "Chave primária inválida para esta tabela", 400
            
            where_clause = " AND ".join([f"{key} = %s" for key in composite_keys[table]])
            query = f"DELETE FROM {table} WHERE {where_clause}"
            cur.execute(query, pk_values)
        else:
            # Para chaves simples
            if table not in primary_keys:
                return "Chave primária não definida para esta tabela", 400
            
            pk_column = primary_keys[table]
            query = f"DELETE FROM {table} WHERE {pk_column} = %s"
            cur.execute(query, (pk,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return redirect(url_for('show_table', table=table))
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
            conn.close()
        
        # Tratar erros específicos
        if "foreign key constraint" in str(e).lower():
            error_msg = f"Não é possível deletar este registro pois ele está sendo referenciado por outros dados. Remova primeiro as referências relacionadas."
        else:
            error_msg = f"Erro ao deletar registro: {str(e)}"
        
        return render_template('procedure_error.html', 
                             error_message=error_msg,
                             back_url=url_for('show_table', table=table))
    except Exception as e:
        return f"Erro inesperado: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
