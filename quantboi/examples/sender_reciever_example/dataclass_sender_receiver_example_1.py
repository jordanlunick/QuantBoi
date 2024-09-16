from dataclasses import dataclass

@dataclass
class Sender:
    value: int

@dataclass
class Receiver:
    sender: Sender

    def update_from_sender(self):
        # Update from the sender's current state
        return self.sender.value

# Example usage
sender = Sender(value=10)
receiver = Receiver(sender=sender)

# Update sender value
sender.value = 20

# Receiver pulls the updated value
print(receiver.update_from_sender())  # Outputs: 20
