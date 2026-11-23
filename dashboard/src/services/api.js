const BASE_URL = '';

export async function fetchUserMemories(userId = 'user_default', status = 'active') {
  try {
    const res = await fetch(`${BASE_URL}/users/${userId}/memories?status=${status}`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.memories || [];
  } catch (err) {
    console.error('Error fetching memories:', err);
    return [];
  }
}

export async function fetchUserPolicies(userId = 'user_default') {
  try {
    const res = await fetch(`${BASE_URL}/users/${userId}/policies`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.policies || [];
  } catch (err) {
    console.error('Error fetching policies:', err);
    return [];
  }
}

export async function createPolicy(userId = 'user_default', naturalLanguageRule) {
  try {
    const res = await fetch(`${BASE_URL}/users/${userId}/policies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rule: naturalLanguageRule })
    });
    return await res.json();
  } catch (err) {
    console.error('Error creating policy:', err);
    return null;
  }
}

export async function traceIngestTurn(userId = 'user_default', text, speaker = 'user', sessionId = null) {
  const res = await fetch(`${BASE_URL}/pipeline/ingest-trace`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      speaker: speaker,
      text: text,
      session_id: sessionId
    })
  });
  return await res.json();
}

export async function traceRecallQuery(userId = 'user_default', question) {
  const res = await fetch(`${BASE_URL}/pipeline/recall-trace`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      question: question
    })
  });
  return await res.json();
}

export async function fetchAuditLogs(userId = 'user_default') {
  try {
    const res = await fetch(`${BASE_URL}/users/${userId}/audit`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.logs || [];
  } catch (err) {
    console.error('Error fetching audit logs:', err);
    return [];
  }
}
