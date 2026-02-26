from marketmind_engine.narrative.projection.symbol_extractor import SymbolExtractor


def test_extract_dollar_symbol():
    extractor = SymbolExtractor()
    symbols = extractor.extract("Breaking: $NVDA beats earnings")
    assert "NVDA" in symbols


def test_extract_standalone_symbol():
    extractor = SymbolExtractor()
    symbols = extractor.extract("NVDA surges after report")
    assert "NVDA" in symbols


def test_no_lowercase_false_positive():
    extractor = SymbolExtractor()
    symbols = extractor.extract("Nvidia surges after report")
    assert "NVIDIA" not in symbols


def test_multiple_symbols():
    extractor = SymbolExtractor()
    symbols = extractor.extract("NVDA and AMD rally together")
    assert set(symbols) == {"AMD", "NVDA"}