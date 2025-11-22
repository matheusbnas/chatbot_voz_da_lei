"""
Serviço para pré-processamento e limpeza de textos legislativos
"""
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger


class TextProcessor:
    """Serviço para processar e limpar textos de legislação"""
    
    def __init__(self):
        # Padrões regex para normalização
        self.article_pattern = re.compile(r'Art\.?\s*(\d+)[º°]?', re.IGNORECASE)
        self.paragraph_pattern = re.compile(r'§\s*(\d+)[º°]?', re.IGNORECASE)
        self.inciso_pattern = re.compile(r'([IVX]+|[\d]+)[º°]?\s*-', re.IGNORECASE)
        self.alinea_pattern = re.compile(r'([a-z])\)', re.IGNORECASE)
    
    def parse_xml(self, xml_content: str) -> str:
        """
        Extrair texto de XML, removendo tags e mantendo estrutura
        
        Args:
            xml_content: Conteúdo XML
            
        Returns:
            Texto limpo
        """
        try:
            root = ET.fromstring(xml_content)
            
            # Função recursiva para extrair texto
            def extract_text(element, depth=0):
                text_parts = []
                
                # Adicionar texto do elemento
                if element.text and element.text.strip():
                    text_parts.append(element.text.strip())
                
                # Processar filhos
                for child in element:
                    child_text = extract_text(child, depth + 1)
                    if child_text:
                        text_parts.append(child_text)
                    
                    # Adicionar texto após o filho
                    if child.tail and child.tail.strip():
                        text_parts.append(child.tail.strip())
                
                return " ".join(text_parts)
            
            return extract_text(root)
            
        except ET.ParseError as e:
            logger.error(f"Erro ao parsear XML: {str(e)}")
            # Se não for XML válido, retornar como está
            return xml_content
        except Exception as e:
            logger.error(f"Erro ao processar XML: {str(e)}")
            return xml_content
    
    def normalize_text(self, text: str) -> str:
        """
        Normalizar texto: remover tags, normalizar espaços, etc
        
        Args:
            text: Texto bruto
            
        Returns:
            Texto normalizado
        """
        if not text:
            return ""
        
        # Remover tags HTML/XML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalizar espaços em branco
        text = re.sub(r'\s+', ' ', text)
        
        # Normalizar quebras de linha
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remover caracteres especiais problemáticos
        text = text.replace('\xa0', ' ')  # Non-breaking space
        text = text.replace('\u200b', '')  # Zero-width space
        
        # Normalizar aspas
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def split_into_chunks(
        self,
        text: str,
        chunk_type: str = "article"
    ) -> List[Dict[str, Any]]:
        """
        Dividir texto em chunks (artigos, parágrafos, etc)
        
        Args:
            text: Texto completo
            chunk_type: Tipo de chunk (article, paragraph, inciso)
            
        Returns:
            Lista de chunks com metadados
        """
        chunks = []
        
        if chunk_type == "article":
            # Dividir por artigos
            articles = self.article_pattern.split(text)
            
            for i in range(1, len(articles), 2):
                if i + 1 < len(articles):
                    article_num = articles[i]
                    article_content = articles[i + 1]
                    
                    # Extrair parágrafos do artigo
                    paragraphs = self._extract_paragraphs(article_content)
                    
                    chunks.append({
                        "type": "article",
                        "number": article_num,
                        "content": article_content,
                        "normalized_content": self.normalize_text(article_content),
                        "paragraphs": paragraphs,
                        "metadata": {
                            "has_paragraphs": len(paragraphs) > 0,
                            "paragraph_count": len(paragraphs)
                        }
                    })
        
        elif chunk_type == "paragraph":
            # Dividir por parágrafos
            paragraphs = self._extract_paragraphs(text)
            chunks = [
                {
                    "type": "paragraph",
                    "number": p["number"],
                    "content": p["content"],
                    "normalized_content": self.normalize_text(p["content"]),
                    "metadata": {}
                }
                for p in paragraphs
            ]
        
        else:
            # Chunk único
            chunks.append({
                "type": "full_text",
                "number": None,
                "content": text,
                "normalized_content": self.normalize_text(text),
                "metadata": {}
            })
        
        return chunks
    
    def _extract_paragraphs(self, text: str) -> List[Dict[str, str]]:
        """Extrair parágrafos de um texto"""
        paragraphs = []
        matches = list(self.paragraph_pattern.finditer(text))
        
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            paragraph_text = text[start:end].strip()
            if paragraph_text:
                paragraphs.append({
                    "number": match.group(1),
                    "content": paragraph_text
                })
        
        return paragraphs
    
    def extract_citations(self, text: str) -> List[Dict[str, str]]:
        """
        Extrair citações internas (ex: "Art. 5º", "§ 2º")
        
        Args:
            text: Texto para analisar
            
        Returns:
            Lista de citações encontradas
        """
        citations = []
        
        # Artigos
        for match in self.article_pattern.finditer(text):
            citations.append({
                "type": "article",
                "reference": match.group(0),
                "number": match.group(1)
            })
        
        # Parágrafos
        for match in self.paragraph_pattern.finditer(text):
            citations.append({
                "type": "paragraph",
                "reference": match.group(0),
                "number": match.group(1)
            })
        
        return citations
    
    def process_legislation_text(
        self,
        text: str,
        legislation_id: int
    ) -> List[Dict[str, Any]]:
        """
        Processar texto completo de uma legislação e retornar chunks
        
        Args:
            text: Texto completo da legislação
            legislation_id: ID da legislação
            
        Returns:
            Lista de chunks processados
        """
        # Normalizar texto
        normalized = self.normalize_text(text)
        
        # Dividir em chunks (artigos)
        chunks = self.split_into_chunks(normalized, chunk_type="article")
        
        # Adicionar metadados e citações
        for chunk in chunks:
            chunk["legislation_id"] = legislation_id
            chunk["citations"] = self.extract_citations(chunk["content"])
            chunk["word_count"] = len(chunk["normalized_content"].split())
            chunk["char_count"] = len(chunk["normalized_content"])
        
        return chunks


# Instância global
text_processor = TextProcessor()

