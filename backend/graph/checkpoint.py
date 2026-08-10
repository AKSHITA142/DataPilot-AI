from langgraph.checkpoint.memory import MemorySaver


def get_checkpointer():
    """Returns a MemorySaver checkpointer instance for state checkpointing across node transitions."""
    return MemorySaver()
