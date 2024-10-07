from dataclasses import dataclass

@dataclass
class Sender:
    value: int
    receivers: list = None

    def __post_init__(self):
        if self.receivers is None:
            self.receivers = []

    def register_receiver(self, receiver):
        self.receivers.append(receiver)

    def update_value(self, new_value):
        self.value = new_value
        self.notify_receivers()

    def notify_receivers(self):
        for receiver in self.receivers:
            receiver.pull_from_sender(self)

@dataclass
class Receiver:
    sender_value: int = 0

    def pull_from_sender(self, sender: Sender):
        self.sender_value = sender.value
        print(f'Receiver updated with new value: {self.sender_value}')

# Example usage
sender = Sender(value=10)
receiver = Receiver()

# Link the receiver to the sender
sender.register_receiver(receiver)

# Change the sender value, automatically updating the receiver
sender.update_value(30)  # Outputs: Receiver updated with new value: 30
