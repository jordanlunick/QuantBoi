from dataclasses import dataclass

@dataclass
class Sender:
    value: int

@dataclass
class Receiver:
    sender: Sender

    @property
    def sender_value(self):
        return self.sender.value

# Example usage
sender = Sender(value=10)
receiver = Receiver(sender=sender)

# Change the sender value
sender.value = 50

# Automatically reflect the updated sender value
print(receiver.sender_value)  # Outputs: 50
