import pygame
from pygame.locals import *
from random import randint

pygame.init()

clock = pygame.time.Clock()
fps = 60

largura = 864
altura = 936

tela = pygame.display.set_mode((largura,altura))
pygame.display.set_caption('Flop Bird')

# Texto Fonte
font = pygame.font.SysFont('jetBrains', 60)
# Cores
white = (255, 255, 255)

#Variaveis
terreno_rolagem = 0
velocidade_rolagem = 4
inicio = False
fim_de_jogo = False
cano = 150
cano_freq = 1500  # Milisegundos
último_cano = pygame.time.get_ticks() - cano_freq
placar = 0
passar_cano = False

# Carregando Imagens
fundo = pygame.image.load('img/bg.png')
terreno = pygame.image.load('img/ground.png')
botão = pygame.image.load('img/restart.png')

def mostrar_placar(texto, font, text_color, x, y):
    img = font.render(texto, True, text_color)
    tela.blit(img, (x, y))
    
def reiniciar():
    cano_gp.empty()
    flop.rect.x = 100
    flop.rect.y = int(altura / 2)
    placar = 0
    return placar

class Pássaro(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1,4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.vel = 0
        self.pressionado = False
    
    # Animar imagem    
    def update(self):
        # Gravidade
        if inicio == True:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8            
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)
        if fim_de_jogo == False:
            # Pular
            if pygame.key.get_pressed()[K_UP] == 1 and self.pressionado == False:
                self.pressionado = True
                self.vel = -10
            if pygame.key.get_pressed()[K_UP] == 0:
                self.pressionado = False
            
            # Bater Asas
            self.counter +=1
            flop_fim = 15
            if self.counter > flop_fim:
                self.counter = 0
                self.index +=1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]
            
            # Empinar Bico
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Canos(pygame.sprite.Sprite):
    def __init__(self, x, y, posição):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        
        # Posição 1 = Topo; Posição -1 = Base
        if posição == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(cano / 2)]
        if posição == -1:
            self.rect.topleft = [x, y + int(cano / 2)]
            
    def update(self):
        self.rect.x -= velocidade_rolagem
        if self.rect.right < 0:
            self.kill()
            
class Botão():
    def __init__(self, x, y, imagem):
        self.image = imagem
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
    def mostrar(self):
        
        action = False
        # Posição do mouse
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        
        tela.blit(self.image, (self.rect.x, self.rect.y))
        
        return action

pássaro_gp = pygame.sprite.Group()
cano_gp = pygame.sprite.Group()

flop = Pássaro(100, int(altura / 2))
pássaro_gp.add(flop)

# Criar botão de reiniciar
button = Botão(largura // 2 - 50, altura // 2 - 100, botão)

# ** JOGO **
rodando = True
while rodando:
    
    clock.tick(fps)
    
    # Fundo
    tela.blit(fundo, (0,0))
    
    # Pássaro
    pássaro_gp.draw(tela)
    pássaro_gp.update()
    
    # Canos
    cano_gp.draw(tela)
    
    tela.blit(terreno, (terreno_rolagem, 768))
    
    # Pontuar
    if len(cano_gp) > 0:
        if pássaro_gp.sprites()[0].rect.left > cano_gp.sprites()[0].rect.left and pássaro_gp.sprites()[0].rect.right < cano_gp.sprites()[0].rect.right and passar_cano == False:
            passar_cano = True
        if passar_cano == True:
            if pássaro_gp.sprites()[0].rect.left > cano_gp.sprites()[0].rect.right:
                placar += 1
                passar_cano = False
                
    mostrar_placar(str(placar), font, white, int(largura / 2), 20)
                    
    # Colisão
    if pygame.sprite.groupcollide(pássaro_gp, cano_gp, False, False) or flop.rect.top < 0:
        fim_de_jogo = True
    
    # Tocando o chão
    if flop.rect.bottom >= 768:
        fim_de_jogo = True
        inicio = False
    
    if fim_de_jogo == False and inicio == True:
        # Criar canos
        tempo_atual = pygame.time.get_ticks()
        if tempo_atual - último_cano > cano_freq:
            cano_alt = randint(-100, 100)
            cano_base = Canos(largura, int(altura / 2) + cano_alt, -1)
            cano_topo = Canos(largura, int(altura / 2) + cano_alt, 1)
            cano_gp.add(cano_base)
            cano_gp.add(cano_topo)
            último_cano =tempo_atual
        
        # Terreno rolando
        terreno_rolagem -= velocidade_rolagem
        if abs(terreno_rolagem) > 35:
            terreno_rolagem = 0
        cano_gp.update()
    
    # Reiniciar Jogo
    if fim_de_jogo == True:
        if button.mostrar() == True:
            fim_de_jogo = False
            placar = reiniciar()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        if event.type == pygame.KEYDOWN and inicio == False and fim_de_jogo == False:
            inicio = True
            
    pygame.display.update()
            
pygame.quit()
