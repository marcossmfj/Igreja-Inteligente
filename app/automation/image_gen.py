from PIL import Image, ImageDraw, ImageFont
import os

def generate_schedule_card(member_name: str, position: str, date_str: str, output_path: str, church_slug: str = None):
    """Gera card individual de escala"""
    img = Image.new('RGB', (1080, 1350), color=(30, 27, 75)) # Indigo fundo
    draw = ImageDraw.Draw(img)
    
    # Simulação de layout elegante
    draw.rectangle([50, 50, 1030, 1300], outline=(79, 70, 229), width=10)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 80)
        font_body = ImageFont.truetype("arial.ttf", 50)
    except:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    draw.text((100, 200), "VOCÊ FOI ESCALADO!", fill=(255, 255, 255), font=font_title)
    draw.text((100, 500), f"Membro: {member_name}", fill=(200, 200, 255), font=font_body)
    draw.text((100, 600), f"Função: {position}", fill=(255, 255, 255), font=font_body)
    draw.text((100, 700), f"Data: {date_str}", fill=(200, 200, 255), font=font_body)
    
    img.save(output_path)
    return output_path

def generate_birthday_card(member_name: str, output_path: str):
    """Gera um card individual de aniversário"""
    img = Image.new('RGB', (1080, 1080), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Fundo festivo (simples)
    draw.rectangle([20, 20, 1060, 1060], outline=(255, 215, 0), width=30)
    
    try:
        font_main = ImageFont.truetype("arial.ttf", 90)
        font_sub = ImageFont.truetype("arial.ttf", 60)
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    draw.text((150, 300), "FELIZ", fill=(218, 165, 32), font=font_main)
    draw.text((150, 420), "ANIVERSÁRIO!", fill=(218, 165, 32), font=font_main)
    draw.text((150, 600), f"{member_name}", fill=(30, 27, 75), font=font_sub)
    draw.text((150, 750), "Que Deus te abençoe!", fill=(79, 70, 229), font=font_sub)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    return output_path

def gerar_card_aniversariantes(aniversariantes: list, periodo: str, output_path: str):
    """
    aniversariantes: lista de tuplas [(nome, dia), ...]
    periodo: 'Semana' ou 'Mês'
    """
    img = Image.new('RGB', (1080, 1350), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Header festivo
    draw.rectangle([0, 0, 1080, 300], fill=(79, 70, 229))
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 70)
        font_name = ImageFont.truetype("arial.ttf", 45)
    except:
        font_title = ImageFont.load_default()
        font_name = ImageFont.load_default()

    draw.text((150, 100), f"ANIVERSARIANTES DA {periodo.upper()}", fill=(255, 255, 255), font=font_title)
    
    y = 400
    for nome, dia in aniversariantes:
        draw.text((100, y), f"• {nome}", fill=(30, 27, 75), font=font_name)
        draw.text((850, y), f"Dia {dia}", fill=(79, 70, 229), font=font_name)
        y += 80
        if y > 1200: break # Limite da página
        
    img.save(output_path)
    return output_path
