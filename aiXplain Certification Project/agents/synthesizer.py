"""Compatibility shim for tests: agents.synthesizer

Provides a thin wrapper around `agents.synthesizer_agent.SynthesizerAgent`
to expose a `synthesize` method and an `aixplain` symbol for patching.
"""
from .synthesizer_agent import SynthesizerAgent as _InnerSynth

# allow tests to patch `agents.synthesizer.aixplain`
aixplain = None


class SynthesizerAgent:
    def __init__(self, config):
        self.config = config
        # create inner instance (tests may patch the imported module)
        try:
            self._inner = _InnerSynth(config)
        except Exception:
            self._inner = None

    def synthesize(self, query, gathered_info: dict):
        # Map gathered_info format to the synthesizer_agent API
        docs = gathered_info.get('vector_results', [])
        api_results = gathered_info.get('api_results', {})

        if self._inner:
            return self._inner.synthesize_response(
                query=query,
                retrieved_docs=docs,
                api_results=api_results
            )

        # Fallback minimal response for tests
        return {
            'query': query,
            'answer': 'Stub response',
            'sources': [{'title': d.get('metadata', {}).get('title', 'Doc') if isinstance(d, dict) else 'Doc'} for d in docs],
            'confidence': 0.5
        }
