export async function askQuestion(q) {
  const res = await fetch(`${process.env.REACT_APP_API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: q })
  });
  return res.json();
}
