from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class KnowledgeCase:
    case_id: str
    title: str
    category: str
    symptoms: list[str]
    resolution_summary: str
    full_text: str


class CaseRetriever:
    def __init__(self, cases_path: str | Path = 'data/knowledge_base/cases.jsonl') -> None:
        self.cases_path = Path(cases_path)
        self.cases = self._load_cases()
        corpus = [case.full_text for case in self.cases]
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), min_df=1)
        self.matrix = self.vectorizer.fit_transform(corpus)

    def _load_cases(self) -> list[KnowledgeCase]:
        if not self.cases_path.exists():
            raise FileNotFoundError(f'Knowledge base not found: {self.cases_path}')
        cases: list[KnowledgeCase] = []
        for raw in self.cases_path.read_text(encoding='utf-8').splitlines():
            if not raw.strip():
                continue
            row = json.loads(raw)
            text = ' '.join([
                row['title'],
                row['category'],
                ' '.join(row['symptoms']),
                row['resolution_summary'],
                ' '.join(row.get('keywords', [])),
            ])
            cases.append(
                KnowledgeCase(
                    case_id=row['case_id'],
                    title=row['title'],
                    category=row['category'],
                    symptoms=row['symptoms'],
                    resolution_summary=row['resolution_summary'],
                    full_text=text,
                )
            )
        return cases

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix)[0]
        ranked = sorted(zip(self.cases, scores), key=lambda item: item[1], reverse=True)[:top_k]
        results: list[dict] = []
        for case, score in ranked:
            score_f = round(float(score), 4)
            results.append({
                'case_id': case.case_id,
                'title': case.title,
                'category': case.category,
                'score': score_f,
                'resolution_summary': case.resolution_summary,
                'why_relevant': self._why_relevant(case, query, score_f),
            })
        return results

    @staticmethod
    def _why_relevant(case: KnowledgeCase, query: str, score: float) -> str:
        tokens = set(query.lower().replace('-', ' ').split())
        symptom_text = ' '.join(case.symptoms).lower()
        overlaps = [token for token in tokens if len(token) > 3 and token in symptom_text]
        if overlaps:
            return f"Shared symptom language: {', '.join(sorted(overlaps)[:4])}."
        if score >= 0.4:
            return 'High semantic overlap with the documented case title and resolution summary.'
        return 'Potentially related precedent; validate before using.'
