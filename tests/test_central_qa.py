import pytest
import time
import logging
import uuid
from playwright.sync_api import Page, expect
from app.models import models

# --- CONFIGURAÇÕES GLOBAIS ---
BASE_URL = "http://localhost:8000"
UNIQUE_ID = uuid.uuid4().hex[:6]

# Configurar Logging Profissional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [CENTRAL-QA] - %(message)s')

class ChurchRobot:
    """Page Object Model para o robô de QA centralizado"""
    def __init__(self, page: Page):
        self.page = page

    def setup(self):
        self.page.on("dialog", lambda dialog: dialog.accept())
        self.page.set_default_timeout(30000)

    def login_master(self, user="admin", password="admin"):
        logging.info("Acessando Painel Master...")
        self.page.goto(f"{BASE_URL}/dashboard/master.html")
        self.page.fill('input[placeholder="Admin"]', user)
        self.page.fill('input[placeholder="Senha"]', password)
        self.page.click('button:has-text("Entrar")')
        expect(self.page.locator('h1')).to_contain_text("Painel Master SaaS")

    def create_church_ui(self, name, slug, email, password):
        logging.info(f"Criando igreja via UI: {slug}")
        self.page.fill('input[placeholder="Nome da Igreja"]', name)
        self.page.fill('input[placeholder="Slug (ex: iprv)"]', slug)
        self.page.fill('input[placeholder="E-mail Admin"]', email)
        self.page.fill('input[placeholder="Senha (Nova ou Manter)"]', password)
        self.page.click('button:has-text("Criar Cliente")')
        expect(self.page.locator('div.grid')).to_contain_text(slug)

    def login_pastor(self, slug, email, password):
        logging.info(f"Acessando Dashboard da Igreja: {slug}")
        self.page.goto(f"{BASE_URL}/dashboard/index.html?church={slug}")
        self.page.evaluate("localStorage.clear()")
        self.page.reload()
        self.page.fill('input[placeholder="E-mail"]', email)
        self.page.fill('input[placeholder="Senha"]', password)
        self.page.click('button:has-text("Acessar")')
        expect(self.page.locator('nav h1').first).to_contain_text("Igreja Inteligente")

    def switch_tab(self, tab_name: str):
        self.page.click(f'nav button:has-text("{tab_name}")')
        self.page.wait_for_selector(f'h2:has-text("{tab_name}")', state="visible")

    def register_member(self, name, phone, role_index=1):
        """Cadastra um membro via UI com esperas robustas"""
        btn = self.page.locator('button:has-text("Novo Membro +")')
        btn.wait_for(state="visible")
        btn.click(force=True)
        
        # Esperar o modal abrir e os inputs estarem prontos
        input_name = self.page.locator('input[placeholder="Nome Completo"]')
        input_name.wait_for(state="visible")
        input_name.fill(name)
        
        self.page.fill('input[placeholder*="12345678"]', phone)
        
        # Esperar o select de cargos ter opções (indicando que o backend respondeu)
        select_cargo = self.page.locator('select').first
        select_cargo.wait_for(state="visible")
        # Pequena pausa para o Vue popular o select
        time.sleep(0.5)
        
        # Tentar selecionar a opção
        try:
            self.page.select_option('select >> nth=0', index=role_index)
        except:
            # Se falhar por index, tenta o primeiro disponível
            self.page.select_option('select >> nth=0', index=1)
        
        self.page.click('button:has-text("Finalizar Cadastro")')
        input_name.wait_for(state="hidden")
        time.sleep(0.5)

    def register_visitor(self, name, phone):
        """Cadastra um visitante via UI com esperas robustas"""
        btn = self.page.locator('button:has-text("Novo Visitante +")')
        btn.wait_for(state="visible")
        btn.click(force=True)
        
        input_visitor = self.page.locator('input[placeholder="Nome do Visitante"]')
        input_visitor.wait_for(state="visible")
        input_visitor.fill(name)
        self.page.fill('input[placeholder="WhatsApp"]', phone)
        
        self.page.click('button:has-text("Registrar Entrada")')
        input_visitor.wait_for(state="hidden")
        time.sleep(0.5)

    def create_manual_schedule(self, event_name, date_str):
        """Cria uma escala manual simples via UI com espera de carregamento"""
        self.page.click('#btn-manual-escala', force=True)
        self.page.wait_for_selector('input[placeholder="Nome do Evento"]', state="visible")
        self.page.fill('input[placeholder="Nome do Evento"]', event_name)
        self.page.fill('input[type="datetime-local"]', date_str)
        
        # Seleciona o primeiro cargo
        self.page.select_option('select >> nth=0', index=1) 
        
        # Esperar que o segundo select (membros) tenha opções além da padrão "Selecione..."
        select_membro = self.page.locator('select >> nth=1')
        select_membro.wait_for(state="visible")
        
        # Forçar uma pequena espera para o backend preencher a lista de membros qualificados
        time.sleep(1)
        
        try:
            self.page.select_option('select >> nth=1', index=1, force=True)
            self.page.click('button:has-text("Salvar Escala")', force=True)
            self.page.wait_for_selector('input[placeholder="Nome do Evento"]', state="hidden")
        except Exception as e:
            logging.warning(f"Não foi possível selecionar membro para a escala {event_name}: {e}")
            self.page.keyboard.press("Escape") # Fecha o modal se falhar

# --- TESTES DE SIMULAÇÃO COMPLETA ---

@pytest.mark.playwright
def test_simulate_two_churches_with_data(page: Page):
    """
    Simula 2 igrejas completas com sufixo único para evitar duplicidade.
    """
    SIM_ID = uuid.uuid4().hex[:4]
    bot = ChurchRobot(page)
    bot.setup()
    
    # 1. CRIAR AS IGREJAS NO MASTER
    bot.login_master()
    igrejas = [
        {"nome": f"Igreja Alpha {SIM_ID}", "slug": f"alpha-{SIM_ID}", "email": f"pastor-a-{SIM_ID}@test.com"},
        {"nome": f"Igreja Beta {SIM_ID}", "slug": f"beta-{SIM_ID}", "email": f"pastor-b-{SIM_ID}@test.com"}
    ]
    
    for igr in igrejas:
        bot.create_church_ui(igr["nome"], igr["slug"], igr["email"], "123456")

    # 2. POPULAR CADA IGREJA
    for igr in igrejas:
        bot.login_pastor(igr["slug"], igr["email"], "123456")
        
        # --- MEMBROS (10) ---
        bot.switch_tab("Membros")
        cargos = ["Pastor", "Diácono", "Obreiro", "Levita", "Músico", "Porteiro", "Secretário", "Tesoureiro", "Líder", "Membro"]
        for i in range(10):
            # No cadastro de membros, o select pode estar oculto inicialmente
            btn = page.locator('button:has-text("Novo Membro +")')
            btn.click(force=True)
            page.wait_for_selector('input[placeholder="Nome Completo"]', state="attached")
            page.fill('input[placeholder="Nome Completo"]', f"{cargos[i]} {igr['nome']}")
            page.fill('input[placeholder*="12345678"]', f"551199999{i:04d}")
            
            # Forçar seleção mesmo se "oculto"
            page.select_option('select', index=1, force=True)
            page.click('button:has-text("Finalizar Cadastro")', force=True)
            time.sleep(0.3)
        
        # --- VISITANTES (10) ---
        bot.switch_tab("Visitantes")
        for i in range(10):
            page.click('button:has-text("Novo Visitante +")', force=True)
            page.wait_for_selector('input[placeholder="Nome do Visitante"]', state="attached")
            page.fill('input[placeholder="Nome do Visitante"]', f"Visitante {i+1} {igr['nome']}")
            page.fill('input[placeholder="WhatsApp"]', f"551188888{i:04d}")
            page.click('button:has-text("Registrar Entrada")', force=True)
            time.sleep(0.3)
            
        # --- ESCALAS (2) ---
        bot.switch_tab("Escalas")
        eventos = [
            {"nome": "Culto de Domingo", "data": "2026-05-10T19:00"},
            {"nome": "Reunião de Oração", "data": "2026-05-13T20:00"}
        ]
        for ev in eventos:
            bot.create_manual_schedule(ev["nome"], ev["data"])
            
        logging.info(f"✅ Igreja {igr['nome']} populada!")

    logging.info(f"🚀 SIMULAÇÃO {SIM_ID} FINALIZADA!")

