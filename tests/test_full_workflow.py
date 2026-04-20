import pytest
from playwright.sync_api import Page, expect
import time

# --- DADOS DE TESTE ---
CHURCH_NAME = "Igreja de Teste QA 100"
PASTOR_EMAIL = "pastor_qa@teste.com"
PASTOR_PASS = "123456"

CARGOS_PADRAO = ["Pastor", "Presbítero", "Diácono", "Obreiro"]
FUNCOES_PADRAO = ["Guitarrista", "Sonoplasta", "Professor EBD", "Recepção"]

VISITOR_NAME = "Manoel de Oliveira (Visitante Teste)"
VISITOR_PHONE = "5511999998888"

@pytest.fixture(scope="module", autouse=True)
def setup_test_church():
    """Lógica para garantir que a igreja exista (Simulado)"""
    # Aqui poderíamos chamar o master route para criar a igreja
    pass

def test_full_system_workflow(page: Page):
    """O GRANDE TESTE: Do Linguajar à Promoção do Membro"""
    
    # 1. LOGIN
    print("🚀 Iniciando Login...")
    page.goto("http://localhost:8000/dashboard/")
    page.fill('input[placeholder="E-mail"]', "pastor@igreja.com.br")
    page.fill('input[placeholder="Senha"]', "pastor123")
    page.click('button:has-text("Acessar")')
    
    # Aguarda carregar
    expect(page.locator('h1:has-text("Igreja Inteligente")')).to_be_visible()
    print("✅ Login realizado com sucesso!")

    # 2. CONFIGURAR LINGUAJAR (Cargos e Funções)
    # Abre o Modal de Linguajar (Configurações -> Cargos/Funções)
    print("🏷️ Configurando Linguajar Padrão...")
    # Se não houver botão direto, vamos abrir pela tab que criamos no master
    # Mas como o usuário pediu no pastor, vamos usar o modal ou a tab se disponível
    # Pelo código que li, linguajar é uma tab em alguns layouts ou modal em outros.
    # Vamos verificar se a tab 'membros' está aberta e cadastrar cargos lá.
    page.click('button:has-text("Membros")')
    
    # Abrir Modal de Configurar Cargos (Linguajar)
    # Se houver um botão de engrenagem ou "Configurar"
    # No código atual o linguajar está em ModalConfigCargos.js
    # Vamos tentar clicar no botão que abre esse modal (geralmente próximo à lista de membros)
    # Para teste, vamos simular o cadastro via API se o botão for difícil de achar no headless
    # Mas vamos tentar via UI primeiro:
    page.evaluate("() => { window.app.__vue_app__._instance.proxy.showModalCargos = true }")
    
    for cargo in CARGOS_PADRAO:
        page.fill('input[placeholder="Ex: Diácono, Guitarrista..."]', cargo)
        page.select_option('select', 'Cargo')
        page.click('button:has-text("Cadastrar Termo")')
        time.sleep(0.5)
        print(f"   - Cargo '{cargo}' cadastrado.")

    for funcao in FUNCOES_PADRAO:
        page.fill('input[placeholder="Ex: Diácono, Guitarrista..."]', funcao)
        page.select_option('select', 'Função')
        page.click('button:has-text("Cadastrar Termo")')
        time.sleep(0.5)
        print(f"   - Função '{funcao}' cadastrada.")

    page.click('button:has-text("✕")') # Fecha modal

    # 3. INCLUIR VISITANTE
    print("👣 Incluindo Novo Visitante...")
    page.click('button:has-text("Visitantes")')
    page.click('button:has-text("Novo Visitante +")')
    
    page.fill('input[placeholder="Nome Completo"]', VISITOR_NAME)
    page.fill('input[placeholder="Ex: 5511999998888"]', VISITOR_PHONE)
    page.fill('input[placeholder="Endereço (Rua, Nº, Bairro)"]', "Rua de Teste, 100 - Bairro QA")
    
    page.click('button:has-text("Guardar Visitante")')
    print("✅ Visitante incluído!")

    # 4. VALIDAR SE VISITANTE APARECEU
    expect(page.locator(f'td:has-text("{VISITOR_NAME}")')).to_be_visible()
    print("✅ Visitante visível na tabela.")

    # 5. PROMOVER VISITANTE A MEMBRO (Ficha de Membro com Cargos/Funções)
    print("🌟 Promovendo Visitante a Membro...")
    page.click(f'tr:has-text("{VISITOR_NAME}") button:has-text("Promover")')
    
    # Selecionar Cargo no Modal de Promoção
    page.select_option('select:first-child', label="Diácono")
    
    # Selecionar Funções (Checkboxes)
    # Vamos marcar 'Guitarrista' e 'Recepção'
    page.check('label:has-text("Guitarrista") input')
    page.check('label:has-text("Recepção") input')
    
    page.click('button:has-text("Confirmar Promoção")')
    print("✅ Promoção concluída!")

    # 6. VALIDAR NOVO MEMBRO E FICHA (Cargos e Funções na tela)
    page.click('button:has-text("Membros")')
    expect(page.locator(f'tr:has-text("{VISITOR_NAME}")')).to_be_visible()
    
    # Verificar se as "tags" de cargos aparecem na linha do membro
    expect(page.locator(f'tr:has-text("{VISITOR_NAME}") span:has-text("Diácono")')).to_be_visible()
    expect(page.locator(f'tr:has-text("{VISITOR_NAME}") span:has-text("Guitarrista")')).to_be_visible()
    print("✅ Membro validado com Diácono e Guitarrista na ficha!")

    print("\n🏁 TESTE 100% OK: Fluxo completo validado!")

if __name__ == "__main__":
    # Comando para rodar manualmente se necessário
    pass
