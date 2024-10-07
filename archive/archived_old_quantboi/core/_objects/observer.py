import logging
import QuantLib as ql
from typing import List




# /// QuantLib Wrappers /// #
class ObserverWrapper(ql.Observer):
    def __init__(self):
        def callback():
            self.update()
        super().__init__(callback)

    def update(self) -> None:
        """Override the update method with custom logic."""
        #logging.info("ConcreteObserver has been notified!")


# /// Subject Class /// #
class Observer:
    def __init__(self):
        self._observers: List[ql.Observer] = []

    def register_observer(self, observer: ql.Observer) -> None:
        """Register an observer."""
        if observer not in self._observers:
            self._observers.append(observer)
            #logging.info(f"Observer {observer} registered.")
        else:
            pass#logging.warning(f"Observer {observer} is already registered.")
            

    def unregister_observer(self, observer: ql.Observer) -> None:
        """Unregister an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
            #logging.info(f"Observer {observer} unregistered.")
        else:
            pass#logging.warning(f"Observer {observer} is not registered.")
            

    def notify_observers(self) -> None:
        """Notify all registered observers."""
        #logging.info(f"Notifying {len(self._observers)} observers.")
        for observer in self._observers:
            observer.update()


