from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models import models
from app.core import security
import sys

def setup():
    db = SessionLocal()
    try:
        # 1. CRIAR IGREJA MASTER (SaaS)
        master_church = db.query(models.Church).filter(models.Church.slug == "master").first()
        if not master_church:
            master_church = models.Church(
                name="SaaS Administrador Master", 
                slug="master", 
                subscription_status="active"
            )
            db.add(master_church)
            db.commit()
            db.refresh(master_church)
            print("✅ Igreja Master Criada!")

        # 2. CRIAR USUÁRIO MASTER (Acesso Master e SaaS)
        master_email = "admin@igreja.com.br"
        master_user = db.query(models.User).filter(models.User.email == master_email).first()
        if not master_user:
            master_user = models.User(
                email=master_email,
                name="Administrador Master",
                hashed_password=security.get_password_hash("admin123"), # SENHA PADRÃO
                church_id=master_church.id,
                is_admin=True,
                is_master=True
            )
            db.add(master_user)
            db.commit()
            print(f"✅ Usuário Master Criado: {master_email} / Senha: admin123")
        else:
            print(f"⚠️ Usuário Master já existia ({master_email})")

        # 3. CRIAR IGREJA DE TESTE (Portal do Pastor)
        test_church = db.query(models.Church).filter(models.Church.slug == "igreja-teste").first()
        if not test_church:
            test_church = models.Church(
                name="Igreja de Teste Local", 
                slug="igreja-teste", 
                subscription_status="active"
            )
            db.add(test_church)
            db.commit()
            db.refresh(test_church)
            print("✅ Igreja de Teste Criada!")

        # 4. CRIAR USUÁRIO PASTOR (Acesso Portal do Pastor)
        pastor_email = "pastor@igreja.com.br"
        pastor_user = db.query(models.User).filter(models.User.email == pastor_email).first()
        if not pastor_user:
            pastor_user = models.User(
                email=pastor_email,
                name="Pastor de Teste",
                hashed_password=security.get_password_hash("pastor123"), # SENHA PADRÃO
                church_id=test_church.id,
                is_admin=True,
                is_master=False
            )
            db.add(pastor_user)
            db.commit()
            print(f"✅ Usuário Pastor Criado: {pastor_email} / Senha: pastor123")
        else:
            print(f"⚠️ Usuário Pastor já existia ({pastor_email})")

        # 5. CADASTRAR CARGOS E FUNÇÕES PADRÃO (Para teste)
        cargos_padrao = [
            ("Pastor", models.PositionType.CARGO),
            ("Obreiro", models.PositionType.CARGO),
            ("Diácono", models.PositionType.CARGO),
            ("Membro", models.PositionType.FUNCAO),
            ("Músico", models.PositionType.FUNCAO),
            ("Mídia", models.PositionType.FUNCAO),
            ("Som", models.PositionType.FUNCAO),
            ("Recepção", models.PositionType.FUNCAO)
        ]
        
        for name, p_type in cargos_padrao:
            existing = db.query(models.Position).filter(
                models.Position.name == name, 
                models.Position.church_id == test_church.id
            ).first()
            if not existing:
                new_pos = models.Position(name=name, type=p_type, church_id=test_church.id)
                db.add(new_pos)
        
        db.commit()
        print("✅ Cargos e Funções Padrão Adicionados à Igreja de Teste!")

    except Exception as e:
        print(f"❌ Erro no setup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    setup()
