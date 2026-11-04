"""A complete change video for a fictional business."""
from deck import S, opens, rows
SLUG = "quillback-parts-reorder"; TITLE = "Parts reorder"; FOOT = "Quillback Marine | Parts reorder"
SCENES = [
    S("a", "paper", "This change adds a reorder button to every part. It drafts the purchase order, and a person still sends it.",
      ["adds", "drafts", "person"],
      rows("What changed", [(1, "Reorder button", "On every part in Inventory.", False), (2, "The draft", "Vendor, quantity and price filled in.", False), (3, "The gate", "Staff send it. The agent can't.", False)]), "Running on a preview"),
    S("b", "umber", "One thing to decide. Should a reorder under fifty dollars send without asking?",
      ["reorder"],
      opens([(1, "Small reorders", "Send without asking under $50?")], (1, "Say yes to ship this as it is."), "Your call"), "Waiting on your yes"),
]
