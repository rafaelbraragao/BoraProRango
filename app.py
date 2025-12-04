# 📦 Bibliotecas padrão
import os
import uuid
import json
import random
from datetime import datetime
from collections import defaultdict
from extensoes import db  # ✅ importa do novo módulo

# 🌐 Bibliotecas externas
from utils import gerar_qr_code_pix
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask
from flask_login import current_user
from flask import current_app
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from dotenv import load_dotenv
import requests
import mercadopago
from itsdangerous import URLSafeTimedSerializer

# 🧩 Módulos do projeto
from utils import gerar_token, validar_token
from config import DevelopmentConfig, ProductionConfig, TestingConfig
from models import db, Usuario, Oferta, Pagamento
from decorators import login_required, admin_required
from models import Usuario, Oferta, Pagamento  # ✅ agora pode impo

# 🔁 Detecta o ambiente e carrega o .env correspondente
load_dotenv()
env = os.getenv('FLASK_ENV', 'development')
if env == 'production':
    load_dotenv('.env.prod')
elif env == 'testing':
    load_dotenv('.env.test')
else:
    load_dotenv('.env')


# 🚀 Inicializa o app
app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))

# 🔧 Aplica a configuração correta
if env == 'production':
    app.config.from_object(ProductionConfig)
elif env == 'testing':
    app.config.from_object(TestingConfig)
else:
    app.config.from_object(DevelopmentConfig)

# 🔐 Chave secreta
app.secret_key = app.config['SECRET_KEY']


# 📬 Inicializa o Flask-Mail
mail = Mail(app)

# 🛢️ Inicializa o banco de dados
db.init_app(app)
migrate = Migrate(app, db)

# 📁 Configura uploads
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 💳 Configura Mercado Pago
ambiente_mp = os.getenv("MERCADO_PAGO_ENV", "sandbox")
if ambiente_mp == "production":
    public_key = os.getenv("MP_PUBLIC_KEY_PRODUCTION")
    access_token = os.getenv("MP_ACCESS_TOKEN_PRODUCTION")
else:
    public_key = os.getenv("MP_PUBLIC_KEY_SANDBOX")
    access_token = os.getenv("MP_ACCESS_TOKEN_SANDBOX")

# Verificação de segurança: checa se o token está ausente ou se é um token live em ambiente de sandbox
if not access_token or (not access_token.startswith("TEST-") and ambiente_mp != "production"):
    raise RuntimeError("Access token inválido ou ausente. Verifique o .env. Se estiver em 'sandbox', use um token que comece com 'TEST-'.")

# ✅ CORREÇÃO AQUI: Usa a variável Python 'access_token' que já contém o token correto
#sdk = mercadopago.SDK(access_token)
sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN_SANDBOX"))

# 🔐 Serializer para tokens de recuperação de senha
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
# --- FIM DA CONFIGURAÇÃO ---
@app.route('/webhook', methods=['POST'])
def webhook():
    # 🔐 Validação do token de segurança
    token_recebido = request.args.get("token")
    if token_recebido != os.getenv("WEBHOOK_TOKEN"):
        print("Token inválido recebido no webhook")
        return '', 403

    # ✅ Se o token for válido, continua o processamento
    data = request.get_json()
    print("Webhook recebido:", data)

    if data.get("type") == "payment":
        payment_id = data.get("data", {}).get("id")
        if payment_id:
            try:
                payment_info = sdk.payment().get(payment_id)
                status = payment_info["response"]["status"]
                print(f"Status atualizado via webhook: {status}")

                pagamento = Pagamento.query.filter_by(payment_id=str(payment_id)).first()
                if pagamento:
                    pagamento.status = status
                    db.session.commit()
                    print(f"Pagamento {payment_id} atualizado para {status}")
                else:
                    print(f"Pagamento {payment_id} não encontrado no banco")

            except Exception as e:
                print(f"Erro ao buscar pagamento: {e}")

    return '', 200
 
# Página principal de pagamento
@app.route('/pagamento/<payment_id>')
@login_required
def pagamento_pix(payment_id):
    pagamento = Pagamento.query.filter_by(payment_id=payment_id).first_or_404()
    # Aqui você chamaria a API Pix para gerar o QR Code
    qr_code_url = gerar_qr_code_pix(pagamento.payment_id, pagamento.valor)
    return render_template('pagamento_pix.html', qr_code=qr_code_url, valor=pagamento.valor)

@app.route("/pagamento", methods=["GET", "POST"])
def pagamento():
    contexto = {}

    if request.method == "POST":
        valor = request.form.get("valor", "50.00")
        contexto["valor_pix"] = valor

        payment_data = {
            "transaction_amount": float(valor),
            "description": "Pagamento via PIX",
            "payment_method_id": "pix",
            "payer": {
                "email": "rafaelbraragao@gmail.com",
                "first_name": "Rafael",
                "last_name": "Teste",
                "identification": {
                    "type": "CPF",
                    "number": "19119119100"
                }
            }
        }

        response = sdk.payment().create(payment_data)
        payment = response.get("response", {})
        status = response.get("status")

        print(json.dumps(payment, indent=2))

        if status != 201 or "point_of_interaction" not in payment:
            contexto.update({
                "status_pagamento": "erro",
                "payment_id": None
            })
        else:
            dados = payment["point_of_interaction"]["transaction_data"]
            contexto.update({
                "status_pagamento": "sucesso",
                "qr_code_base64": dados["qr_code_base64"],
                "chave_pix": dados["qr_code"],
                "payment_id": payment["id"]
            })

    return render_template("pagamento.html", **contexto)
# Simular aprovação de pagamento (sandbox)
@app.route("/simular_pagamento", methods=["POST"])
def simular_pagamento():
    payment_id = request.form.get("payment_id")

    try:
        # Atualiza o status no banco de dados local
        pagamento = Pagamento.query.filter_by(payment_id=payment_id).first()
        if pagamento:
            pagamento.status = "approved"
            db.session.commit()
        else:
            print(f"Pagamento com ID {payment_id} não encontrado.")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao simular pagamento: {e}")

    return redirect(f"/verificar_pagamento?payment_id={payment_id}")
# Verificar status do pagamento
@app.route("/verificar_pagamento", methods=["GET"])
def verificar_pagamento():
    payment_id = request.args.get("payment_id")

    try:
        payment_response = sdk.payment().get(payment_id)
        print("🔍 Resposta completa do Mercado Pago:")
        print(json.dumps(payment_response, indent=2, ensure_ascii=False))

        payment = payment_response.get("response", {})
        status_pagamento = payment.get("status")

        if not status_pagamento:
            raise ValueError("Resposta do Mercado Pago não contém 'status'.")

        # Atualiza o status no banco
        pagamento = Pagamento.query.filter_by(payment_id=str(payment_id)).first()
        if pagamento:
            pagamento.status = status_pagamento
            db.session.commit()
            print(f"✅ Pagamento {payment_id} atualizado para {status_pagamento}")
        else:
            print(f"⚠️ Pagamento {payment_id} não encontrado no banco.")

    except Exception as e:
        print(f"❌ Erro ao verificar pagamento: {e}")

    # Redireciona de volta para a lista de pagamentos
    return redirect("/admin/pagamentos")
@app.route("/meus_pagamentos")
@login_required
def meus_pagamentos():
    pagamentos = Pagamento.query.filter_by(usuario_id=current_user.id).order_by(Pagamento.criado_em.desc()).all()
    return render_template("meus_pagamentos.html", pagamentos=pagamentos)

@app.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar():
    erro = None

    if request.method == 'POST':
        preco = request.form['preco'].strip()
        endereco = request.form['endereco'].strip()
        telefone = request.form['telefone'].strip()
        rango = request.form.get('rango', '').strip()
        imagem = request.files.get('imagem')

        if not preco or not endereco or not telefone or not rango or not imagem:
            erro = 'Todos os campos são obrigatórios, incluindo a imagem.'
            return render_template('cadastrar.html', erro=erro)

        if not imagem.filename.lower().endswith(('.jpg', '.jpeg')):
            erro = 'Apenas arquivos JPG são permitidos.'
            return render_template('cadastrar.html', erro=erro)

        imagem.seek(0, os.SEEK_END)
        tamanho = imagem.tell()
        imagem.seek(0)

        if tamanho > 2 * 1024 * 1024:
            erro = 'A imagem deve ter no máximo 2MB.'
            return render_template('cadastrar.html', erro=erro)

        ext = os.path.splitext(imagem.filename)[1]
        nome_arquivo = secure_filename(f"{uuid.uuid4().hex}{ext}")
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)

        try:
            imagem.save(caminho)
        except Exception as e:
            erro = f'Erro ao salvar imagem: {e}'
            print(f"ERRO DE ARQUIVO: {e}")
            return render_template('cadastrar.html', erro=erro)

        try:
            # Cria a oferta com status pendente (ainda sem payment_id)
            nova_oferta = Oferta(
                preco=preco,
                endereco=endereco,
                telefone=telefone,
                rango=rango,
                imagem=nome_arquivo,
                usuario_id=session['usuario_id'],
                status_pagamento='pendente'
            )
            db.session.add(nova_oferta)
            db.session.flush()

            # Cria o pagamento via Mercado Pago
            payment_data = {
                "transaction_amount": float(preco),
                "description": "Pagamento via PIX",
                "payment_method_id": "pix",
                "payer": {
                    "email": "rafaelbraragao@gmail.com",
                    "first_name": "Rafael",
                    "last_name": "Teste",
                    "identification": {
                        "type": "CPF",
                        "number": "19119119100"
                    }
                }
            }

            response = sdk.payment().create(payment_data)
            payment = response.get("response", {})
            status = response.get("status")

            if status != 201 or "point_of_interaction" not in payment:
                raise Exception("Erro ao gerar pagamento no Mercado Pago")

            payment_id = str(payment["id"])

            # Atualiza a oferta com o payment_id
            nova_oferta.payment_id = payment_id

            # Cria o registro de pagamento no banco
            pagamento = Pagamento(
                payment_id=payment_id,
                valor=float(preco),
                status='pendente',
                usuario_id=session['usuario_id'],
                oferta_id=nova_oferta.id
            )
            db.session.add(pagamento)
            db.session.commit()

            # Extrai dados do QR Code
            dados = payment["point_of_interaction"]["transaction_data"]
            chave_pix = dados["qr_code"]
            qr_code_base64 = dados["qr_code_base64"]

            return render_template(
                'pagamento.html',
                payment_id=payment_id,
                chave_pix=chave_pix,
                qr_code_base64=qr_code_base64,
                valor_pix=preco,
                status_pagamento='sucesso'
            )

        except Exception as e:
            db.session.rollback()
            erro = f"Erro ao cadastrar oferta: {e}"
            print(f"ERRO SQLALCHEMY: {e}")

    return render_template('cadastrar.html', erro=erro)

@app.route('/', endpoint='pagina_principal')
def mostrar_pagina_principal():
    busca = request.args.get('busca', '').strip()

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    por_pagina = 6

    # 1. Query base
    query = Oferta.query

    # 2. Filtro por título
    if busca:
        query = query.filter(Oferta.rango.ilike(f'%{busca}%'))

    # 3. Ordenação
    query = query.order_by(Oferta.data_criacao.desc())

    # 4. Paginação
    total = query.count()
    total_paginas = (total + por_pagina - 1) // por_pagina
    ofertas_query = query.offset((page - 1) * por_pagina).limit(por_pagina).all()

    # 5. Limite por usuário
    limite_por_usuario = 3
    ofertas_por_usuario = defaultdict(list)

    for oferta in ofertas_query:
        if len(ofertas_por_usuario[oferta.usuario_id]) < limite_por_usuario:
            ofertas_por_usuario[oferta.usuario_id].append(oferta)

    ofertas_filtradas = []
    for lista in ofertas_por_usuario.values():
        ofertas_filtradas.extend(lista)

    random.shuffle(ofertas_filtradas)

    # 6. Dados para o template
    ofertas = [{
        'rango': o.rango,
        'preco': o.preco,
        'endereco': o.endereco,
        'telefone': o.telefone,
        'imagem': o.imagem,
        'rango': o.rango,  # ✅ agora incluído
        'data_criacao': o.data_criacao.strftime('%d/%m/%Y %H:%M') if o.data_criacao else 'N/A'
    } for o in ofertas_filtradas]

    # 7. Renderiza a página
    return render_template(
        'index.html',
        ofertas=ofertas,
        page=page,
        total_paginas=total_paginas,
        busca=busca
    )


               
               
# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_id' in session:
        # Redireciona com base no tipo de usuário já logado
        usuario = Usuario.query.get(session['usuario_id'])
        if usuario and usuario.is_admin:
            return redirect(url_for('listar_usuarios'))
        else:
            return redirect(url_for('admin'))

    erro = None

    if request.method == 'POST':
        email = request.form['email'].strip()
        senha = request.form['senha']

        user = Usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha, senha):
            print(f"Login bem-sucedido: {user.email}")
            print(f"is_admin: {user.is_admin} (tipo: {type(user.is_admin)})")
            session['usuario_id'] = user.id
            session['usuario_nome'] = user.nome
            session['usuario_avatar'] = getattr(user, 'avatar', '')

            if user.is_admin:
                return redirect(url_for('listar_usuarios'))
            else:
                return redirect(url_for('admin'))
        else:
            erro = 'E-mail ou senha inválidos.'

    return render_template('login.html', erro=erro)

@app.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            token = serializer.dumps(email, salt='recuperar-senha')
            base_url = current_app.config['BASE_URL']
            link = f"{base_url}/redefinir-senha/{token}"

            msg = Message('Redefinição de Senha',
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[usuario.email])
            msg.body = f'Olá, {usuario.nome}!\n\nClique no link abaixo para redefinir sua senha:\n{link}\n\nSe você não solicitou isso, ignore este e-mail.'
            mail.send(msg)

            flash('Um link de redefinição foi enviado para seu e-mail.', 'info')
        else:
            flash('E-mail não encontrado.', 'warning')

        return redirect(url_for('esqueci_senha'))

    return render_template('esqueci_senha.html', mensagem='Verifique seu e-mail!')

@app.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    email = validar_token(token)
    if not email:
        flash('Link expirado ou inválido.')
        return redirect(url_for('esqueci_senha'))

    if request.method == 'POST':
        nova_senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            usuario.senha = generate_password_hash(nova_senha)
            db.session.commit()
            flash('Senha atualizada com sucesso!')
            return redirect(url_for('login'))
    return render_template('redefinir_senha.html', mensagem='Senha atualizada com sucesso!')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    usuario_id = session['usuario_id']
    oferta = Oferta.query.get(id)

    # Verifica se a oferta existe e pertence ao usuário
    if not oferta or oferta.usuario_id != usuario_id:
        return "Acesso não autorizado", 403

    if request.method == 'POST':
        rango = request.form['rango'].strip()
        preco = request.form['preco'].strip()
        endereco = request.form['endereco'].strip()
        telefone = request.form['telefone'].strip()
        prato = request.form.get('prato')  # Novo campo

        # Atualiza os campos
        oferta.rango = rango
        oferta.preco = preco
        oferta.endereco = endereco
        oferta.telefone = telefone
        oferta.prato = prato  # Atualiza o prato selecionado

        try:
            db.session.commit()
            return redirect('/admin')
        except Exception as e:
            db.session.rollback()
            return f"Erro ao atualizar oferta: {e}", 500

    # GET request: prepara dados para o formulário
    dados_oferta = {
        'rango': oferta.rango,
        'preco': oferta.preco,
        'endereco': oferta.endereco,
        'telefone': oferta.telefone,
        'prato': oferta.rango  # Inclui o prato atual
    }

    return render_template('editar.html', oferta=dados_oferta)

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    # Impede que usuários já logados acessem a página de registro
    if 'usuario_id' in session:
        usuario = Usuario.query.get(session['usuario_id'])
        if usuario and usuario.is_admin:
            return redirect(url_for('listar_usuarios'))
        else:
            return redirect(url_for('admin'))

    erro = None

    if request.method == 'POST':
        nome = request.form['nome'].strip()
        email = request.form['email'].strip()
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha)

        avatar_arquivo = request.files.get('avatar')
        avatar_url = ''
        if avatar_arquivo and avatar_arquivo.filename != '':
            nome_arquivo = secure_filename(avatar_arquivo.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
            try:
                avatar_arquivo.save(caminho)
                avatar_url = nome_arquivo
            except Exception as e:
                erro = f'Erro ao salvar avatar: {e}'
                print(f"ERRO DE ARQUIVO: {e}")

        try:
            novo_usuario = Usuario(
                nome=nome,
                email=email,
                senha=senha_hash,
                avatar=avatar_url
            )
            db.session.add(novo_usuario)
            db.session.commit()
            return redirect('/login')
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed' in str(e):
                erro = 'E-mail já cadastrado.'
            else:
                erro = f'Ocorreu um erro no registro: {e}'
            print(f"ERRO SQLALCHEMY: {e}")

    return render_template('registrar.html', erro=erro)

from decorators import login_required  # Certifique-se de importar seu decorador

@app.route('/editar_usuario', methods=['GET', 'POST'])
@login_required
def editar_usuario():
    usuario = Usuario.query.get(session['usuario_id'])

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        avatar = request.files.get('avatar')

        # Atualiza os campos
        usuario.nome = nome
        usuario.email = email
        if senha:
            usuario.senha = generate_password_hash(senha)

        if avatar and avatar.filename != '':
            filename = secure_filename(avatar.filename)
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            avatar.save(caminho)
            usuario.avatar = filename
            session['usuario_avatar'] = filename  # Atualiza a sessão

        db.session.commit()
        session['usuario_nome'] = nome
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('admin'))

    return render_template('editar_registro.html', usuario=usuario)
# Rota de logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
# Rota para excluir oferta
@app.route('/excluir/<int:id>')
@login_required
def excluir(id):
    usuario_id = session['usuario_id']

    # Busca a oferta pelo ID
    oferta = Oferta.query.get(id)

    if not oferta:
        return "Oferta não encontrada", 404

    if oferta.usuario_id != usuario_id:
        return "Acesso não autorizado", 403

    try:
        db.session.delete(oferta)
        db.session.commit()
        return redirect(url_for('admin'))
    except Exception as e:
        db.session.rollback()
        return f"Erro ao excluir oferta: {e}", 500

# Painel de administração
@app.route('/admin')
@login_required
def admin():
    usuario_id = session['usuario_id']

    # Consulta usando SQLAlchemy
    ofertas_query = Oferta.query.filter_by(usuario_id=usuario_id).all()

    # Converte os objetos em dicionários para o template
    ofertas = []
    for o in ofertas_query:
        ofertas.append({
            'id': o.id,
            'rango': o.rango,
            'preco': o.preco,
            'endereco': o.endereco,
            'telefone': o.telefone,
            'imagem': o.imagem,
            'cidade': o.cidade,
            'prato': o.rango # ✅ campo adicionado
        })

    return render_template('admin.html', ofertas=ofertas)



@app.route("/admin/pagamentos")
def listar_pagamentos():
    pagamentos = Pagamento.query.order_by(Pagamento.criado_em.desc()).all()
    print("Pagamentos encontrados:", pagamentos)
    return render_template("admin_pagamentos.html", pagamentos=pagamentos)

@app.route('/admin/usuarios/promover/<int:id>', methods=['POST'])
@admin_required
def promover_usuario(id):
    admin = Usuario.query.get(session['usuario_id'])
    if not admin or not admin.is_admin:
        abort(403)

    usuario = Usuario.query.get_or_404(id)
    usuario.is_admin = True

    # Atualiza a sessão se o usuário promovido for o logado
    if usuario.id == session.get('usuario_id'):
        session['usuario_is_admin'] = True

    db.session.commit()
    return redirect(url_for('listar_usuarios'))

@app.route('/admin/usuarios/excluir/<int:id>', methods=['POST'])
def excluir_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('listar_usuarios'))

@app.route('/admin/usuarios')
@admin_required
def listar_usuarios():
    
    usuario_logado = Usuario.query.get(session['usuario_id'])
    if not usuario_logado or not usuario_logado.is_admin:
        abort(403)

    termo = request.args.get('busca', '').strip()

    if termo:
        usuarios = Usuario.query.filter(
            (Usuario.nome.ilike(f'%{termo}%')) | (Usuario.email.ilike(f'%{termo}%'))
        ).all()
    else:
        usuarios = Usuario.query.all()

    return render_template('admin_usuarios.html', usuarios=usuarios, termo=termo)
@app.route('/admin/apagar_ofertas')
@admin_required
def apagar_ofertas():
    Oferta.query.delete()
    db.session.commit()
    return 'Todas as ofertas foram apagadas com sucesso.'

@app.route('/admin/limpar_ofertas_orfas')
@admin_required
def limpar_ofertas_orfas():
    try:
        db.session.query(Oferta).filter(
            ~Oferta.usuario_id.in_(db.session.query(Usuario.id))
        ).delete(synchronize_session=False)
        db.session.commit()
        return 'Ofertas órfãs apagadas com sucesso.'
    except Exception as e:
        db.session.rollback()
        return f'Erro ao apagar ofertas órfãs: {e}', 500
    
@app.errorhandler(403)
def acesso_negado(e):
    return render_template('403.html'), 403

@app.route('/teste-email')
def teste_email():
    from flask_mail import Message

    msg = Message(
        subject='🔧 Teste de E-mail Flask',
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[app.config['MAIL_USERNAME']],  # envia para você mesmo
        body='Este é um e-mail de teste enviado pelo Flask-Mail. Se você recebeu isso, está tudo funcionando! 🚀'
    )

    try:
        mail.send(msg)
        return '✅ E-mail de teste enviado com sucesso!'
    except Exception as e:
        return f'❌ Falha ao enviar e-mail: {str(e)}'
    
@app.route('/teste')
def teste():
    return {
        'status': 'ok',
        'versao': '1.0.0',
        'usuario_logado': 'usuario_id' in session
    }
if __name__ == '__main__':
    app.run(debug=True)