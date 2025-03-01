# similarity_calculator.py

import numpy as np
import heapq


class SimilarityCalculator:
    @staticmethod
    def cosine_similarity(vec1, vec2):
        a = np.array(vec1).ravel()
        b = np.array(vec2).ravel()
        denom = np.sqrt(np.sum(np.square(vec1))) * np.sqrt(np.sum(np.square(vec2)))
        return np.dot(a, b) / denom

    @staticmethod
    def similar_players(vectors: dict, index: int) -> dict:
        similarity_scores = {}
        for k, v in vectors.items():
            similarity_scores[k] = SimilarityCalculator.cosine_similarity(vectors[index], v)
        similarity_scores = {key: value for key, value in similarity_scores.items()}
        return similarity_scores
