from src.agents.genie_agent import classify_and_explain

SAFE = """function transfer(address to, uint256 amount) public {
    require(balances[msg.sender] >= amount, "Insufficient");
    balances[to] += amount;
    balances[msg.sender] -= amount;
}
"""

UNSAFE = """function transfer(address to, uint256 amount) public {
    balances[to] += amount;
    balances[msg.sender] -= amount;
}
"""

def test_safe_detection():
    r = classify_and_explain(SAFE)
    assert r["status"] == "safe"
    assert r["citation_line"] is not None

def test_unsafe_detection():
    r = classify_and_explain(UNSAFE)
    assert r["status"] == "unsafe"
    assert r["citation_line"] is None
