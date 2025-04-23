import cv2
import numpy as np
import pytesseract
from sklearn.neighbors import KDTree
from collections import defaultdict

class FlowchartReader:
    def __init__(self, image_path):
        self.image_path = image_path
        self.original_img = None
        self.processed_img = None
        self.shapes = []
        self.arrows = []
        self.flowchart = {"nodes": [], "connections": []}
        
        # Configurações do Tesseract
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
    def preprocess_image(self):
        """Carrega e pré-processa a imagem"""
        self.original_img = cv2.imread(self.image_path)
        gray = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, self.processed_img = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)
        
    def detect_elements(self):
        """Detecta todos os elementos do fluxograma"""
        self._detect_shapes()
        self._detect_arrows()
        self._extract_text()
        
    def _detect_shapes(self):
        """Detecta formas geométricas principais"""
        contours, _ = cv2.findContours(self.processed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 500:  # Ignora pequenos ruídos
                continue
                
            approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
            epsilon = 0.1 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            
            shape_type = self._classify_shape(approx)
            moments = cv2.moments(cnt)
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])
            
            self.shapes.append({
                "contour": cnt,
                "type": shape_type,
                "approx": approx,
                "centroid": (cx, cy),
                "text": "",
                "bounding_box": cv2.boundingRect(cnt)
            })
    
    def _classify_shape(self, approx):
        """Classifica a forma com base nos vértices"""
        vertices = len(approx)
        
        if vertices == 3:
            return "triangle"
        elif vertices == 4:
            # Distinguir entre retângulo e losango
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w)/h
            if 0.8 <= aspect_ratio <= 1.2:
                return "diamond"
            return "rectangle"
        elif vertices == 5:
            return "pentagon"
        elif vertices >= 8:
            return "circle"
        return "polygon"
    
    def _detect_arrows(self):
        """Detecta setas usando análise de linhas e pontas"""
        edges = cv2.Canny(self.processed_img, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=30, maxLineGap=10)
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                if length > 20:  # Filtra linhas muito curtas
                    # Verifica se é uma seta (ponta triangular)
                    arrow_tip = self._find_arrow_tip((x1, y1), (x2, y2))
                    if arrow_tip:
                        self.arrows.append({
                            "start": (x1, y1),
                            "end": (x2, y2),
                            "tip": arrow_tip
                        })
    
    def _find_arrow_tip(self, start, end):
        """Identifica a ponta da seta"""
        # Implementação simplificada - pode ser melhorada
        return end  # Nesta versão, assumimos que o final da linha é a ponta
    
    def _extract_text(self):
        """Extrai texto de cada forma detectada"""
        for shape in self.shapes:
            x, y, w, h = shape["bounding_box"]
            roi = self.original_img[y:y+h, x:x+w]
            
            # Pré-processamento da ROI para OCR
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            _, binary_roi = cv2.threshold(gray_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Configuração do OCR para melhor precisão
            custom_config = r'--oem 3 --psm 6 -l por+eng'
            text = pytesseract.image_to_string(binary_roi, config=custom_config).strip()
            shape["text"] = text
    
    def build_flowchart(self):
        """Constrói a estrutura lógica do fluxograma"""
        # Cria nós
        for i, shape in enumerate(self.shapes):
            self.flowchart["nodes"].append({
                "id": i,
                "type": shape["type"],
                "text": shape["text"],
                "position": shape["centroid"],
                "bounding_box": shape["bounding_box"]
            })
        
        # Conecta nós baseado nas setas
        if not self.arrows:
            return
            
        # Cria KDTree para busca eficiente de nós próximos
        positions = [node["position"] for node in self.flowchart["nodes"]]
        kdtree = KDTree(positions)
        
        for arrow in self.arrows:
            start, end = arrow["start"], arrow["end"]
            
            # Encontra os nós mais próximos do início e fim da seta
            _, start_idx = kdtree.query([start], k=1)
            _, end_idx = kdtree.query([end], k=1)
            
            self.flowchart["connections"].append({
                "from": int(start_idx[0][0]),
                "to": int(end_idx[0][0]),
                "type": "arrow"
            })
    
    def visualize(self):
        """Visualiza os elementos detectados"""
        img = self.original_img.copy()
        
        # Desenha formas
        for shape in self.shapes:
            color = (0, 255, 0) if shape["type"] != "diamond" else (255, 0, 0)
            cv2.drawContours(img, [shape["contour"]], -1, color, 2)
            cv2.putText(img, shape["text"], shape["centroid"], 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        
        # Desenha setas
        for arrow in self.arrows:
            cv2.line(img, arrow["start"], arrow["end"], (0, 0, 255), 2)
            if "tip" in arrow:
                cv2.circle(img, arrow["tip"], 3, (0, 0, 255), -1)
        
        cv2.imshow("Flowchart Detection", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def get_flowchart_json(self):
        """Retorna a representação JSON do fluxograma"""
        return self.flowchart

# Exemplo de uso
if __name__ == "__main__":
    reader = FlowchartReader("fluxograma_exemplo.png")
    reader.preprocess_image()
    reader.detect_elements()
    reader.build_flowchart()
    
    print("Estrutura do Fluxograma:")
    print(reader.get_flowchart_json())
    
    # Visualização (opcional)
    reader.visualize()
    
