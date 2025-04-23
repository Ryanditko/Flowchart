📋 Processador de Fluxogramas por Imagem
Converta imagens de fluxogramas em dados estruturados automaticamente!

Esta ferramenta Python processa imagens de fluxogramas, detectando formas (retângulos, losangos, etc.), setas e textos, convertendo-os em uma estrutura JSON que representa a lógica do fluxograma.

🚀 Funcionalidades
Detecção de formas: Identifica elementos de fluxograma (processos, decisões, terminais) usando OpenCV

Extração de texto: Lê textos dentro das formas usando Tesseract OCR (suporte a múltiplos idiomas)

Conexões inteligentes: Mapeia setas para criar relações entre nós

Visualização: Opção para exibir elementos detectados na imagem original

Saída estruturada: Gera JSON pronto para conversão em Graphviz ou automação de processos

💻 Instalação
Instale as dependências:

bash
pip install opencv-python numpy pytesseract scikit-learn
Instale o Tesseract OCR (necessário para extração de texto)

🛠 Como Usar
python
from flowchart_reader import FlowchartReader

# Processa imagem do fluxograma
reader = FlowchartReader("seu_fluxograma.png")
reader.process()  # Detecta elementos e constrói estrutura

# Obtém os dados estruturados
dados_fluxograma = reader.get_flowchart_json()

# Visualiza detecção (opcional)
reader.visualize()

🌟 Recursos Avançados
Detecção personalizada: Extensível para novos símbolos de fluxograma

Suporte multilíngue: Configurável para diferentes idiomas

Opções de exportação: Em breve - suporte para Graphviz (.dot) e Mermaid.js

📌 Roadmap
Melhor detecção de pontas de seta
Suporte a PDF como entrada
Versão com interface web
