from abc import ABC, abstractmethod

from marketmind_engine.execution.execution_types import OrderIntent
from marketmind_engine.execution.execution_receipt import ExecutionReceipt


class BrokerAdapter(ABC):
    """
    Abstract transport interface to any broker.

    This layer:
    - Talks to external APIs
    - Handles authentication
    - Handles network I/O
    - Returns normalized ExecutionReceipt

    This layer must NOT:
    - Contain trading logic
    - Inspect rules
    - Compute risk
    - Override intent
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def submit(self, order_intent: OrderIntent) -> ExecutionReceipt:
        """
        Submit an order to the broker.

        Must:
        - Be synchronous
        - Return normalized ExecutionReceipt
        - Never return raw SDK objects
        """
        pass
