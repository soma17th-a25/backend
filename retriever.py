import json
import os
from typing import List, Dict, Union

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

class LawRetriever:
    def __init__(self, vector_store_dir: str = "dbvector"):
        """
        LAW Retriever 초기화
        
        Args:
            vector_store_dir: FAISS 인덱스와 메타데이터 저장 경로
        """
        self.vector_store_dir = vector_store_dir
        self.index_path = os.path.join(vector_store_dir, "law_index.faiss")
        self.metadata_path = os.path.join(vector_store_dir, "law_metadata.json")
        
        # FAISS 인덱스 로드
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(f"인덱스 파일 검색 실패: {self.index_path}")
        self.index = faiss.read_index(self.index_path)
        
        # 메타데이터 로드
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(f"메타 데이터 검색 실패: {self.metadata_path}")
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
        
        # 임베딩 모델 로드
        self.model = SentenceTransformer(model)

    def normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """벡터 정규화 (FAISS IndexFlatIP 사용)"""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def search_by_vector(self, query_vector: Union[List[float], np.ndarray], k: int = 3) -> List[Dict]:
        """
        벡터 기반 검색
        
        Args:
            query_vector: 임베딩된 쿼리 벡터 (list 또는 numpy array)
            k: 반환할 상위 결과 개수
            
        Returns:
            검색 결과 리스트 (law, article, title, summary, score 포함)
        """
        if isinstance(query_vector, list):
            query_vector = np.array([query_vector], dtype=np.float32)
        else:
            query_vector = np.array([query_vector], dtype=np.float32)
        
        query_vector = self.normalize_vector(query_vector[0])
        query_vector = np.array([query_vector], dtype=np.float32)
        
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= 0:
                meta = self.metadata[idx]
                results.append({
                    "id": meta["id"],
                    "law": meta["law"],
                    "article": meta["article"],
                    "title": meta["title"],
                    "summary": meta["summary"],
                    "topic": meta["topic"],
                    "keywords": meta.get("keywords", []),
                    "score": float(distance),
                })
        
        return results

    def search_by_text(self, query_text: str, k: int = 3) -> List[Dict]:
        """
        텍스트 기반 검색
        
        Args:
            query_text: 검색 질문 텍스트
            k: 반환할 상위 결과 개수
            
        Returns:
            검색 결과 리스트
        """
        query_vector = self.model.encode(query_text, convert_to_numpy=True)
        return self.search_by_vector(query_vector, k)

    def search_by_topic(self, topic: str, k: int = 3) -> List[Dict]:
        """
        주제별 검색
        
        Args:
            topic: 검색할 주제 (예: '뺑소니', '역주행', '음주운전' 등)
            k: 반환할 상위 결과 개수
            
        Returns:
            주제별 필터링된 결과
        """
        filtered_results = [m for m in self.metadata if m.get("topic") == topic]
        
        if not filtered_results:
            return []
        
        # 주제별 결과가 있으면 상위 k개 반환
        return filtered_results[:k]

    def batch_search(self, query_vectors: List[Union[List[float], np.ndarray]], k: int = 3) -> List[List[Dict]]:
        """
        배치 검색 (여러 쿼리 한번에 처리)
        
        Args:
            query_vectors: 쿼리 벡터 리스트
            k: 반환할 상위 결과 개수
            
        Returns:
            검색 결과 리스트의 리스트
        """
        results = []
        for qv in query_vectors:
            results.append(self.search_by_vector(qv, k))
        return results


def main():
    """테스트용 예제"""
    retriever = LawRetriever()
    
    print("=" * 60)
    print("테스트 1: 텍스트 기반 검색")
    print("=" * 60)
    query = "뺑소니 처벌"
    results = retriever.search_by_text(query, k=3)
    print(f"Query: {query}\n")
    for i, result in enumerate(results, 1):
        print(f"[{i}] {result['law']} - {result['article']} {result['title']}")
        print(f"    Summary: {result['summary']}")
        print(f"    Score: {result['score']:.4f}\n")
    
    print("=" * 60)
    print("테스트 2: 주제별 검색")
    print("=" * 60)
    topic = "역주행"
    topic_results = retriever.search_by_topic(topic)
    print(f"Topic: {topic}\n")
    for i, result in enumerate(topic_results, 1):
        print(f"[{i}] {result['law']} - {result['article']} {result['title']}")
        print(f"    Summary: {result['summary']}\n")


if __name__ == "__main__":
    main()
