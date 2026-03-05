class ContextMapper:

    MAP = {
        "markets": ["earnings", "sector", "guidance"],
        "geopolitics": ["military", "diplomatic", "alliance"]
    }

    @staticmethod
    def get_signals(domain):
        return ContextMapper.MAP.get(domain, [])
